import "dotenv/config";
import OpenAI from "openai";

const openai = new OpenAI({
  baseURL: "https://openrouter.ai/api/v1",
  apiKey: process.env.OPENROUTER_API_KEY,
  // baseURL: process.env.HUGGING_FACE_URL,
  // apiKey: process.env.HUGGING_FACE_API_KEY,
  defaultHeaders: {
    "HTTP-Referer": "<YOUR_SITE_URL>", // Optional. Site URL for rankings on openrouter.ai.
    "X-Title": "<YOUR_SITE_NAME>", // Optional. Site title for rankings on openrouter.ai.
  },
});

async function main() {
  const completion = await openai.chat.completions.create({
    model: "openrouter/auto", // OpenRouter auto selects the model
    messages: [
      {
        role: "user",
        content: "What are you?",
      },
    ],
    temperature: 0.3,
    top_p: 0.6,
  });

  console.log(completion.choices[0].message);
}

main();
