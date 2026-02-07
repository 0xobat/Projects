# ETH trading bot with leverage

## Overview

> Goal: Use DeFi utilities to make money off the swings of the price of ethereum.
> Target Leverage: 10 times.
> Target Profit: 5%
> Resources: Liniux-Backup/My_works/Operations/Blockchain/Trading/Testing

### Utiliies

Lending: Aave
Swaps: Uniswap, Balalncer
Price check: Coinbase
Wallet: New hot wallet with Trust wallet

## Strategies

- Shorting
- Going long

### Short Algorithm

On a collateralized lending platform (aave):

1. Deposit USDC as collateral.
2. Borrow ETH
3. Swap the borrowed ETH for USDC
4. Deposit the USDC from step 3 as more collateral
5. Repeat steps 2 to 4 XX times (XX is the leveage rate)
6. Hold until ETH to USDC percent drops below the target profit margin
7. Sell the amount of USDC to close the entire ETH position.
8. Send 10% of the profit to 0xProfit wallet.

### Long Algorithm

On a collateralized lending platform (aave):

1. Deposit ETH
2. Borrow USDC
3. Swap the borrowed USDC for ETH.
4. Deposit the ETH from step 3 as more collateral
5. Repeat steps 2 to 4 XX times (XX is the leveage rate)
6. Hold until ETH to USDC percent rises above the target profit margin
7. Sell the amount of ETH to close the entire USDC position
8. Send 10% of the profit to 0xProfit wallet.

### NOTE

- Fees: Gas, Swap fees (spread)
- Borrowing Costs

## Mathematical Verification (Proof)
