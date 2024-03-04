# Let's optimize the provided code with the suggestions mentioned.

import pandas as pd
import cudf
from scipy.spatial.distance import mahalanobis
import pandas as pd
 
import numpy
import csv
from memory_profiler import profile

def mahalanobis_gpu(x, y, inv_cov):
    delta = x - y
    return cp.sqrt(cp.dot(cp.dot(delta, inv_cov), delta))
@profile
def main():
    # Load the data
    patents = cudf.read_csv('sharepatARS2_small.csv')
    patents = patents.head(1000000)

    # Convert data types to more memory-efficient formats
    patents['share_pat'] = patents['share_pat'].astype(cp.float32)
    patents['publn_nr'] = patents['publn_nr'].astype(str)
    patents['permno_adj'] = patents['permno_adj'].astype(str)
    patents['publn_year'] = patents['publn_year'].astype(str)

    # Preprocessing that's common across all patents
    num_of_digits = patents['publn_nr'].str.len().max()
    patents['publn_nr'] = patents['publn_nr'].str.slice(0, num_of_digits)
    patents['firmA_yearX'] = patents['permno_adj'] + patents['publn_year']

    # Preprocess for matrix creation
    patents = patents[['publn_nr', 'firmA_yearX', 'IPC1', 'share_pat']].dropna().drop_duplicates().reset_index(drop=True)
    ipc_codes = patents['IPC1'].astype('category').cat.codes
    publn_nr_codes = patents['publn_nr'].astype('category').cat.codes

    # Create and populate the matrix
    patents_pd = patents.to_pandas()

    # Use Pandas to compute unique values
    unique_ipc = len(patents_pd['IPC1'].unique())
    unique_publn_nr = len(patents_pd['publn_nr'].unique())
    patent_matrix_gpu = cp.zeros((unique_ipc, unique_publn_nr), dtype=cp.float32)

    for i, row in enumerate(patents.to_pandas().itertuples()):
        ipc_index = ipc_codes[i]
        publn_nr_index = publn_nr_codes[i]
        patent_matrix_gpu[ipc_index, publn_nr_index] = row.share_pat

    # Compute covariance matrix using cuPy
    cov_matrix_gpu = cp.cov(patent_matrix_gpu, rowvar=True)
    regularization_value = 1e-5
    regularized_cov_matrix_gpu = cov_matrix_gpu + cp.eye(cov_matrix_gpu.shape[0]) * regularization_value
    inv_cov_matrix_gpu = cp.linalg.inv(regularized_cov_matrix_gpu)
    print(f'Completed the inverse calculation')
    # Map IPC classes to indices
    ipc_to_index = {ipc: index for index, ipc in enumerate(patents_pd['IPC1'].unique())}
    num_ipc_classes = len(ipc_to_index)
    
    # Vector construction for each firmA_yearX and patentJ
    firm_vectors = {firmA_yearX: np.zeros(num_ipc_classes) for firmA_yearX in patents_pd['firmA_yearX'].unique()}
    patent_vectors = {patentJ: np.zeros(num_ipc_classes) for patentJ in patents_pd['publn_nr'].unique()}
    
    # Populate firm_vectors and patent_vectors using patents_pd
    for firmA_yearX in firm_vectors.keys():
        firm_data = patents_pd[patents_pd['firmA_yearX'] == firmA_yearX]
        for row in firm_data.itertuples():
            ipc_index = ipc_to_index[row.IPC1]
            firm_vectors[firmA_yearX][ipc_index] = row.share_pat
    
    for patentJ in patent_vectors.keys():
        patent_data = patents_pd[patents_pd['publn_nr'] == patentJ]
        for row in patent_data.itertuples():
            ipc_index = ipc_to_index[row.IPC1]
            patent_vectors[patentJ][ipc_index] = row.share_pat
    del patents_pd
    print(f'Completed creating the vectors')
    # Calculate Mahalanobis distance
    mahalanobis_results_gpu = [
        [firmA_yearX, patentJ, mahalanobis_gpu(firm_vector_gpu, patent_vector_gpu, inv_cov_matrix_gpu)]
        for firmA_yearX, firm_vector_gpu in firm_vectors.items()
        for patentJ, patent_vector_gpu in patent_vectors.items()
    ]
    print('Completed the distance calculations')
    # Convert the results into a DataFrame and save
    mahalanobis_df = pd.DataFrame(mahalanobis_results_gpu, columns=['firmA_yearX', 'patentJ_publn_nr', 'Mahalanobis_Distance'])
    mahalanobis_df.to_csv(f'mahalanobis_gpu.csv', index=False)
main()
# Note: Ensure that the file 'MainfilrARS2_share.csv' is available in the working directory for this script to run correctly.
# Also, the script assumes that the structure of data in 'MainfilrARS2_share.csv' matches the expected format used in the code.

