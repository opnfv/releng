# This is an example of usage of this Tool
# Author: Jose Lausuch (jose.lausuch@ericsson.com)

import opnfv.log_fetcher.LogFetcher

fetcher = LogFetcher(installer='fuel',
                     installer_ip='10.20.0.2',
                     installer_user='root',
                     installer_pwd='r00tme')


fetcher.fetch_all_logs()