# MPTCP_PROJECT_CS179i
This project was developed for the CS179 Senior Design Class at UCR

Enclosed is a number of python scripts using the Python API for mininet alongside the mptcp kernel implementation and the PCC-Project's PCC Vivace Kernel Module.
The first of these scripts attempts to test the performance of popular congestion control protocols on a simple topology with 2, 3, 4, 10, & 20 subflows, and compares it to normal SPTCP.
The second set of scripts attempts to test the performance of MPTCP vs SPTCP when the loss % on the link increases.
The final set of scripts attempts to test the fairness of MPTCP when there exists multiple hosts/clients on the subflow paths.
