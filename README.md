# ModelTraderRequesting
## Requesting history with an end date
* for hourly you need to specify the hour past with 00 for minutes
* e.g. if you want through the 7 hour you would specifiy 2019, 8, 22, 8, 0 for the enddatetime
* for 15 mins you have to go to the next qtr hour to get the prior
* .e.g specify 2019,8,22,9,0 for 8:45 for the enddatetime
* Daily have to specify the day you want
* e.g. specify 2019,8,21,0,0 for day information on 8/21

## The key is made up of the following categories
* 0 - long/short
* 1 - ATR15
* 2 - ATR1
* 3 - ATRD
* 4 - CCI15
* 5 - CCIA15
* 6 - CCIA1h
* 7 - CCIA1d
* 8 - BBW15
* 9 - BBb15
* 10 - BBW1h
* 11 - BBb1h
* 12 - BBW1d
* 13 - BBb1d

Items 8 - 13 is only used for CCI with Bollinger Bands