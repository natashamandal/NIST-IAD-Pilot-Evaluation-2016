import pandas as pd
import sys
zonepath = sys.argv[1]
sidx = zonepath.rfind("/", 0, zonepath.rfind("/"))
zoneid = zonepath[sidx+1:-1]
zone_timestamps = pd.read_csv(zonepath + "timestamp.tsv",
                       na_values=['-'], sep='\t', names = ['timestamp'])
zone_flow_df = pd.read_csv(zonepath + "flow.tsv",
                     na_values=['-'], sep='\t')
num_cols = len(zone_flow_df.columns)
def isNaN(x):
    return (x == x) == False
flow_arr = []

for i in range(num_cols):
    flow_arr.insert(i,'f_d'+str(i+1))
    
zone_flow_df = pd.read_csv(zonepath + "flow.tsv",
                     na_values=['-'], sep='\t', names = flow_arr)
speed_arr = []

for i in range(num_cols):
    speed_arr.insert(i,'s_d'+str(i+1))
	
zone_speed_df = pd.read_csv(zonepath + "speed.tsv",
                     na_values=['-'], sep='\t', names = speed_arr)

occ_arr = []

for i in range(num_cols):
    occ_arr.insert(i,'o_d'+str(i+1))
	
zone_occupancy_df = pd.read_csv(zonepath + "occupancy.tsv",
                     na_values=['-'], sep='\t', names = occ_arr )

prob_arr = []

for i in range(num_cols):
    prob_arr.insert(i,'p_d'+str(i+1))

zone_prob_df = pd.read_csv(zonepath + "prob.tsv",
                     na_values=['-'], sep='\t', names = prob_arr)

zone_flow_df_m1 = zone_flow_df
zone_flow_df_m1 = pd.concat([zone_flow_df_m1,zone_prob_df],axis=1)

for i in range(num_cols):
    j = i+1
    fdj = 'f_d'+`j`
    zone_flow_df_m1[fdj] = zone_flow_df_m1[fdj].fillna(0.0).astype(int)

from scipy import stats
for i in range(num_cols):
    j = i+1
    fdj = 'f_d'+`j`
    cdj = 'c_d'+`j`
    if(num_cols == 1):
        zone_flow_df_m1['pf_d1'] = zone_flow_df_m1['f_d1']
        zone_flow_df_m1[cdj] = zone_flow_df_m1['p_d1']
        break;
    elif(i==0):
        flow_x = zone_flow_df_m1['f_d2']
        conf = zone_flow_df_m1['p_d2']
    elif(i==num_cols-1):
        flow_x = zone_flow_df_m1['f_d'+`i`]
        conf = zone_flow_df_m1['p_d'+`j`]
    else:
        flow_x = (zone_flow_df_m1['f_d'+`i`] + zone_flow_df_m1['f_d'+`i+2`])/2
        conf = (zone_flow_df_m1['p_d'+`j-1`]+zone_flow_df_m1['p_d'+`j+1`])/2
        
    slope, intercept, r_value, p_value, std_err = stats.linregress(flow_x,zone_flow_df_m1[fdj])
    zone_flow_df_m1['p'+fdj] = slope*flow_x + intercept
    zone_flow_df_m1[cdj] = conf
	
result = pd.DataFrame()

for i in range(num_cols):
    j = i+1
    fdj = 'f_d'+str(j)
    sdj = 's_d'+str(j)
    odj = 'o_d'+str(j)
    pdj = 'p_d'+str(j)
    zone_j_vector = pd.concat([zone_flow_df[fdj], zone_speed_df[sdj], zone_occupancy_df[odj], zone_prob_df[pdj], zone_timestamps['timestamp'] ], axis=1)
    is_f_Nan = ~isNaN(zone_j_vector[fdj])
    zone_j_vector = zone_j_vector[is_f_Nan]
    is_s_Nan = ~isNaN(zone_j_vector[sdj])
    zone_j_vector = zone_j_vector[is_s_Nan]
    is_o_Nan = ~isNaN(zone_j_vector[odj])
    zone_j_vector = zone_j_vector[is_o_Nan]
    is_p_Nan = ~isNaN(zone_j_vector[pdj])
    zone_j_vector = zone_j_vector[is_p_Nan]
    is_t_Nan = ~isNaN(zone_j_vector['timestamp'])
    zone_j_vector = zone_j_vector[is_t_Nan]
    zone_j_vector_head = zone_j_vector.head(1)
    is_head = zone_j_vector.index.isin(zone_j_vector_head.index)
    zone_j_vector_tail = zone_j_vector.tail(1)
    is_tail = zone_j_vector.index.isin(zone_j_vector_tail.index)
    zone_j_vector['c1'] = zone_j_vector[pdj].shift()
    zone_j_vector['c2'] = zone_j_vector[pdj].shift(-1)
    zone_j_vector.loc[is_head,'c1'] = 0
    zone_j_vector.loc[is_tail,'c2'] = 0
    zone_j_vector['w1'] = zone_j_vector['c1']/(zone_j_vector['c1']+zone_j_vector['c2'])
    zone_j_vector['w2'] = zone_j_vector['c2']/(zone_j_vector['c1']+zone_j_vector['c2'])
    zone_j_vector['p_m1'] = zone_flow_df_m1['p'+fdj]
    zone_j_vector['c_m1'] = zone_flow_df_m1['c_d'+`j`]
    zone_j_vector['p_m2'] = zone_j_vector[fdj].shift()*zone_j_vector['w1'] + zone_j_vector[fdj].shift(-1)*zone_j_vector['w2']
    zone_j_vector['c_m2'] = zone_j_vector.loc[:, ['c1','c2']].min(axis=1)
    zone_j_vector['p_m3'] = zone_j_vector[fdj]
    zone_j_vector['c_m3'] = zone_j_vector[pdj]
    zone_j_vector.loc[is_head,'p_m2'] = zone_j_vector[pdj]
    zone_j_vector.loc[is_tail,'p_m2'] = zone_j_vector[pdj]
    zone_j_vector['C1'] =  zone_j_vector['c_m1']/(zone_j_vector['c_m1']+zone_j_vector['c_m2'] + zone_j_vector['c_m3'])
    zone_j_vector['C2'] =  zone_j_vector['c_m2']/(zone_j_vector['c_m1']+zone_j_vector['c_m2'] + zone_j_vector['c_m3'])
    zone_j_vector['C3'] =  zone_j_vector['c_m3']/(zone_j_vector['c_m1']+zone_j_vector['c_m2'] + zone_j_vector['c_m3'])
    zone_j_vector['flow_corrected'] = zone_j_vector['C1'] * zone_j_vector['p_m1']+ zone_j_vector['C2'] * zone_j_vector['p_m2'] + zone_j_vector['C3'] * zone_j_vector['p_m3']
    zone_j_vector['flow_corrected'] = zone_j_vector['flow_corrected'].round()
    
    is_within_flow = zone_j_vector[fdj] < 36
    zone_j_vector_within_flow = zone_j_vector[is_within_flow]
    is_within_flow = zone_j_vector_within_flow[fdj] >=0
    zone_j_vector_within_flow = zone_j_vector_within_flow[is_within_flow]
    zone_j_vector.loc[zone_j_vector.index.isin(zone_j_vector_within_flow.index),'flow_corrected'] = zone_j_vector[fdj] 

    is_occupancy_100 = zone_j_vector[odj] == 100
    zone_j_vector_occ_100 = zone_j_vector[is_occupancy_100]
    is_speed_0 = zone_j_vector_occ_100[sdj] == 0
    zone_j_vector_occ_100 = zone_j_vector_occ_100[is_speed_0]
    is_flow_not_0 = zone_j_vector_occ_100[fdj] <> 0
    zone_j_vector_occ_100 = zone_j_vector_occ_100[is_flow_not_0]
    zone_j_vector.loc[zone_j_vector.index.isin(zone_j_vector_occ_100.index),'flow_corrected'] = 0
   
    is_occupancy_0 = zone_j_vector[odj] == 0
    zone_j_vector_occ_0 = zone_j_vector[is_occupancy_0]
    is_speed_0 = zone_j_vector_occ_0[sdj] == 0
    zone_j_vector_occ_0 = zone_j_vector_occ_0[is_speed_0]
    is_flow_not_0 = zone_j_vector_occ_0[fdj] <> 0
    zone_j_vector_occ_0 = zone_j_vector_occ_0[is_flow_not_0]
    zone_j_vector.loc[zone_j_vector.index.isin(zone_j_vector_occ_0.index),'flow_corrected'] = 0
   
    is_flow_corr_Nan = isNaN(zone_j_vector['flow_corrected'])
    zone_j_vector_is_flow_corr_Nan = zone_j_vector[is_flow_corr_Nan]
    zone_j_vector.loc[zone_j_vector.index.isin(zone_j_vector_is_flow_corr_Nan.index), 'flow_corrected'] = zone_j_vector[fdj].median()
    

    result = pd.concat([result, zone_j_vector['flow_corrected']],axis=1)    
   

result.to_csv(zonepath + zoneid+".flow.txt", index=False, header = False)



