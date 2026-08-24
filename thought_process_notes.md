Data Fixing notes.

Missing data in country columns. {small}

We want SA data from S_adjusted because it is seasonally adjusted. 
We want xdc, which is domestic national currency. It should be okay since we are not 
comparing currencies but we are analyzing trends and such. 

For employment we want POP_PCH_PT (Period-over-Preceding-Period Percent Change)
which calculates change from previous rate.

Still require one more operation. I now have two seperatetimeframes, not sure which since I have removed all other columns, still have to investigare further. Add to all countries and i'm good.
Its Keywords[] column, contains two values, Real GDP and GDP at current prices. Keeping REAL GDP then we do calculate the employment one.