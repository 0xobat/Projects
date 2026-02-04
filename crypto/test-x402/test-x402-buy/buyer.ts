import "dotenv/config";
import { privateKeyToAccount } from "viem/accounts";
import { x402Client, x402HTTPClient } from "@x402/axios";
import { registerExactEvmScheme } from "@x402/evm/exact/client";
import axios from "axios";

const signer = privateKeyToAccount(
  process.env.EVM_PRIVATE_KEY as "0x${string}",
);

const client = new x402Client();
registerExactEvmScheme(client, { signer });

const baseURL = "http://0.0.0.0:4021";
const httpClient = new x402HTTPClient(client);

// Step 1: Call the / endpoint (no payment required)
console.log("📍 Calling / endpoint (no payment required)...\n");
const rootResponse = await axios.get(`${baseURL}/`);
console.log("Response from /:", JSON.stringify(rootResponse.data, null, 2));

// Step 2: Call the /weather endpoint to check payment requirements
console.log("\n📍 Calling /weather endpoint to check payment...\n");
try {
  const weatherCheck = await axios.get(`${baseURL}/weather`);
  console.log("Response from /weather:", JSON.stringify(weatherCheck.data, null, 2));
} catch (error: any) {
  if (error.response?.status === 402) {
    console.log("💳 Payment required! Checking payment details...\n");

    // Parse the payment-required header
    const paymentRequiredHeader = error.response.headers["payment-required"];
    if (paymentRequiredHeader) {
      const paymentDetails = JSON.parse(
        Buffer.from(paymentRequiredHeader, "base64").toString()
      );

      console.log("Payment Details:");
      console.log("  Resource:", paymentDetails.resource.description);
      console.log("  URL:", paymentDetails.resource.url);

      if (paymentDetails.accepts && paymentDetails.accepts.length > 0) {
        const paymentOption = paymentDetails.accepts[0];
        const amount = BigInt(paymentOption.amount);
        const tokenName = paymentOption.extra?.name || "tokens";

        // USDC has 6 decimals, so divide by 1e6
        const amountInUSDC = Number(amount) / 1e6;

        console.log("\n💰 Payment Amount:");
        console.log(`  ${amount} ${tokenName} units`);
        console.log(`  ${amountInUSDC} ${tokenName}`);
        console.log("  Pay To:", paymentOption.payTo);
        console.log("  Network:", paymentOption.network);
        console.log("  Asset:", paymentOption.asset);

        // Step 3: Check if amount is less than 0.1 USDC
        const maxAcceptable = 0.1;
        console.log(`\n🔍 Checking if ${amountInUSDC} ${tokenName} < ${maxAcceptable} ${tokenName}...`);

        if (amountInUSDC < maxAcceptable) {
          console.log(`✅ Amount is acceptable! Proceeding with payment...\n`);

          // Make the payment and get the weather data
          const { wrapAxiosWithPayment } = await import("@x402/axios");
          const paidApi = wrapAxiosWithPayment(
            axios.create({ baseURL }),
            client,
          );

          const paidResponse = await paidApi.get("/weather");
          console.log("🌤️  Weather Data:", JSON.stringify(paidResponse.data, null, 2));

          // Parse the payment-response header
          const paymentResponseHeader = paidResponse.headers["payment-response"];
          if (paymentResponseHeader) {
            const paymentConfirmation = JSON.parse(
              Buffer.from(paymentResponseHeader, "base64").toString()
            );

            console.log("\n✅ Payment Confirmed:");
            console.log("  Success:", paymentConfirmation.success);
            console.log("  Payer:", paymentConfirmation.payer);
            console.log("  Transaction:", paymentConfirmation.transaction);
            console.log("  Network:", paymentConfirmation.network);
            console.log("\n  Original Payment:");
            console.log(`    Amount: ${amountInUSDC} ${tokenName}`);
            console.log(`    Recipient: ${paymentOption.payTo}`);
          } else {
            console.log("\n⚠️  No payment-response header found");
          }
        } else {
          console.log(`❌ Amount ${amountInUSDC} ${tokenName} exceeds maximum acceptable ${maxAcceptable} ${tokenName}`);
          console.log("Payment rejected. Not proceeding with request.");
        }
      }
    }
  } else {
    console.error("Unexpected error:", error.message);
    throw error;
  }
}
