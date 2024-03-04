# ip-technical-distance-measure

This script is designed to compute the Mahalanobis distances between patents and their
respective firm-year vectors based on International Patent Classification (IPC) shares. It
operates on two datasets containing patent information and their IPC classifications. This
explanation will guide you through each part of the script, providing a clear understanding of its
function and purpose.

## Overview
The script processes two CSV files:
- MainfilrARS2.csv contains patents with their publication years, firm identifiers
(permno_adj), and IPC codes.

- MainfilrARS2_share.csv includes similar information but adds a share of IPCs for a given
patent, considering the number of IPCs associated with each patent.

# Steps in the Script
Setup and Load Data: Initializes logging for the script and loads the datasets into
Pandas DataFrames. This step is crucial for monitoring the script&#39;s progress and
debugging.
Preprocessing:
● Combines permno_adj and publn_year into a new column, permno_year, in both
datasets. This new column uniquely identifies a firm in a given year, facilitating
later analyses.
Aggregate IPC Shares:
● A function, aggregate_ipc_shares, aggregates IPC shares differently based on
the dataset type (&quot;main&quot; or &quot;share&quot;).
● For &quot;main&quot;, it counts IPC occurrences per firm-year and calculates the share of
each IPC.
● For &quot;share&quot;, it sums up IPC shares per patent within firm-years.
Compute Mahalanobis Distances:
● This function, compute_mahalanobis, calculates the Mahalanobis distance
between each patent&#39;s IPC share vector and its corresponding firm-year IPC
share vector. The distance measures how unusual a patent&#39;s IPC distribution is
compared to the typical IPC distribution of its firm in that year.
● It iterates over each patent, retrieves its IPC share vector and the corresponding
firm-year vector, then calculates the distance using the inverse of the covariance
matrix computed from firm-year vectors.
Yearly Processing:
● The script processes data year by year to manage computational load and
account for yearly variations effectively.
● For each year, it aggregates IPC shares for both patents and firm-years,
computes the covariance matrix (and its inverse) for the firm-year data, and
calculates Mahalanobis distances.

● This approach ensures that the analysis is sensitive to changes in IPC
distributions over time and reduces memory usage.
Results Compilation and Saving:
● All calculated distances are compiled into a single DataFrame, which includes
permno_year, publn_nr (patent number), and the calculated Mahalanobis
distance.
● This DataFrame is then saved to a CSV file, providing a comprehensive overview
of the distance between individual patents and their firm-year vectors.