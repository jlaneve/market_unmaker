### The Market UN-Maker

Please see [our full writeup here]("Exploiting illiquid markets with unlimited capital.pdf").

Optiver has created a virtual exchange titled Optibook, where market participants are allowed to create automated trading bots. For Hack the Burgh 2021, Optiver provided three securities: AMAZON, GOOGLE, and TECH_BASKET. TECH_BASKET functions as a market basket, where the price of the security should be equivalent to the sum of AMAZON and GOOGLE’s individual prices. To our knowledge, Optiver had trading bots providing sufficient liquidity to AMAZON and GOOGLE, as well as trading TECH_BASKET towards the sum of AMAZON and GOOGLE when the prices diverged; however, market participants were asked to create more liquidity for TECH_BASKET.

In the training period, we were able to achieve **$100mm PnL over a time span of ~8 hours**. In the testing period, we achieved **~$45mm over a time span of ~1 hour**. Rather than leaving the bot running, we decided to let it trade for long enough to prove our thesis; we left the bot off for the remainder of the competition.

Through the competition, we learned firsthand why illiquid markets are poor environments for market participants to trade in and why firms like Optiver, among other market makers, are essential to the health of the markets. It was incredible to learn this through an experiential learning exercise rather than through a textbook, and we thank Optiver for access to their platform.