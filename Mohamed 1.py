#!/usr/bin/env python
# coding: utf-8

# In[ ]:
# Let's optimize the provided code with the suggestions mentioned.
import pandas as pd
from scipy.spatial.distance import mahalanobis
import pandas as pd
import numpy as np
import csv

# Load the data
patents = pd.read_csv('shorter_ipc.csv')
patents = patents.rename({'ipc1':'IPC1'}, axis = 1)
# Convert data types to more memory-efficient formats
patents['share_pat'] = patents['share_pat'].astype(np.float32)
patents['publn_nr'] = patents['publn_nr'].astype(str)
patents['permno_adj'] = patents['permno_adj'].astype(str)
patents['publn_year'] = patents['publn_year'].astype(str)

# Preprocessing that's common across all chunks
num_of_digits = patents['publn_nr'].str.len().max()
patents['publn_nr'] = patents['publn_nr'].str.slice(0, num_of_digits)
patents['firmA_yearX'] = patents['permno_adj'] + patents['publn_year']

# Split the data into chunks for memory-efficient processing
num_split = 1
dfs = np.array_split(patents, num_split)

for i, df_chunk in enumerate(dfs):
    # Process each chunk
    chunk = df_chunk[['publn_nr', 'firmA_yearX', 'IPC1', 'share_pat']].dropna().drop_duplicates().reset_index(drop=True)
    
    # Group and create matrices
    grouped_firmA_yearX = chunk.groupby('firmA_yearX')['share_pat'].apply(list)
    grouped_patentJ = chunk.groupby('publn_nr')['share_pat'].apply(list)
    patent_matrix = chunk.pivot_table(index='IPC1', columns='publn_nr', values='share_pat', fill_value=0)

    # Compute covariance matrix
    cov_matrix = np.cov(patent_matrix, rowvar=True)
    regularization_value = 1e-5
    regularized_cov_matrix = cov_matrix + np.eye(cov_matrix.shape[0]) * regularization_value
    inv_cov_matrix = np.linalg.inv(regularized_cov_matrix)
    print(f'Completed the inverse calculation')
    # Map IPC classes to indices
    ipc_to_index = {ipc: index for index, ipc in enumerate(chunk['IPC1'].unique())}
    num_ipc_classes = len(ipc_to_index)
    
    # Vector construction for each firmA_yearX and patentJ
    firm_vectors = {firmA_yearX: np.zeros(num_ipc_classes) for firmA_yearX in grouped_firmA_yearX.keys()}
    patent_vectors = {patentJ: np.zeros(num_ipc_classes) for patentJ in grouped_patentJ.keys()}

    for firmA_yearX, shares in grouped_firmA_yearX.items():
        for ipc, share in zip(chunk.loc[chunk['firmA_yearX'] == firmA_yearX, 'IPC1'], shares):
            if ipc in ipc_to_index:
                firm_vectors[firmA_yearX][ipc_to_index[ipc]] = share

    for patentJ, shares in grouped_patentJ.items():
        for ipc, share in zip(chunk.loc[chunk['publn_nr'] == patentJ, 'IPC1'], shares):
            if ipc in ipc_to_index:
                patent_vectors[patentJ][ipc_to_index[ipc]] = share
    print(f'Completed creating the vectors')
    # Calculate Mahalanobis distance
    mahalanobis_results = [
        [firmA_yearX, patentJ, mahalanobis(firm_vector, patent_vector, inv_cov_matrix)]
        for firmA_yearX, firm_vector in firm_vectors.items()
        for patentJ, patent_vector in patent_vectors.items()
    ]
    print('Completed the distance calculations')
    # Convert the results into a DataFrame and save
    mahalanobis_df = pd.DataFrame(mahalanobis_results, columns=['firmA_yearX', 'patentJ_publn_nr', 'Mahalanobis_Distance'])
    print(len(mahalanobis_df))
    if i == 0:
        mahalanobis_df.to_csv(f'mahalanobis_cpu_check.csv', index=False)
    else:
        mahalanobis_df.to_csv(f'mahalanobis_cpu_check.csv', header=False, mode='a', index=False)

# Note: Ensure that the file 'MainfilrARS2_share.csv' is available in the working directory for this script to run correctly.
# Also, the script assumes that the structure of data in 'MainfilrARS2_share.csv' matches the expected format used in the code.


