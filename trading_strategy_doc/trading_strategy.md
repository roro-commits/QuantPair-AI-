
**
The system was Abstracted from the book Trade like a Hedge Fund by James Altucher 2004
**

For each day, calculate the difference between the ratio and its moving average 
P1 = the most volatile pair
P2 = the most stable pair 
    
### The UNILATERAL PAIRS TRADING SYSTEM FOR QQQ (P1) -SPY (P2) Abstracted.

(1) Calculate the **ratio** of the P1 price series over the P2 price series. 
(2) Calculate the 20-day moving average of that **ratio** .
(3) For each day, calculate the difference between the ratio and its moving average.
(4) Calculate the 20-day moving average of those differences. 
(5) For each day, calculate how many standard deviations the differences in ratio is for that day from the moving
    moving average. Calculate the standard  deviation for each day using it prior 20 days.
(6) For each day, if the standard deviation calculated is greater than 1.5 and P1 is 2 percent greater  than the prior day
    , then P1. (in other words, the spread between P1 and P2 has become much greater than usual. If this is true
    and P1 had a big up move, then QQ ia most likely  the culprit and needs to be Shorted)
(7) For each day, if the standard deviation calculated is less than -1.5 and P1 is 2 percent lowe than the prior day, then buy QQQ.
(8) Sell/Cover when the standard deviation of the difference in the ratio is less than 0.5 (in the case of a short) or greater than -0.5
    (in the case of a long)

This is the system for the unilateral pairs trading and will be represented as a pythons Code.
 
