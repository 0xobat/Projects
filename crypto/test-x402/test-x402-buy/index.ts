import "dotenv/config";
import { privateKeyToAccount } from "viem/accounts";

import { x402Client, wrapAxiosWithPayment, x402HTTPClient } from "@x402/axios";
import { registerExactEvmScheme } from "@x402/evm/exact/client";

import axios from "axios";

const signer = privateKeyToAccount(
  process.env.EVM_PRIVATE_KEY as "0x${string}",
);

const client = new x402Client();
registerExactEvmScheme(client, { signer });

const api = wrapAxiosWithPayment(
  axios.create({ baseURL: "http://0.0.0.0:4021" }),
  client,
);

const response = await api.get("/weather");
console.log("Response:", response.data);

const httpClient = new x402HTTPClient(client);
const paymentResponse = httpClient.getPaymentSettleResponse(
  (name) => response.headers[name.toLowerCase()],
);
console.log("Payment settled:", paymentResponse);
