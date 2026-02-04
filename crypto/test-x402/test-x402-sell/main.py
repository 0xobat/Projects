from typing import Any

from fastapi import FastAPI

from x402.http import FacilitatorConfig, HTTPFacilitatorClient, PaymentOption
from x402.http.middleware.fastapi import PaymentMiddlewareASGI
from x402.http.types import RouteConfig
from x402.mechanisms.evm.exact import ExactEvmServerScheme
from x402.server import x402ResourceServer

app = FastAPI()

## 0x hot
pay_to = "0xf551250f3e2D2A304C3B5EBaE9876f60cDBfD816"

facilitator = HTTPFacilitatorClient(
    FacilitatorConfig(url="https://x402.org/facilitator")
)

server = x402ResourceServer(facilitator)
server.register("eip155:84532", ExactEvmServerScheme())

routes: dict[str, RouteConfig] = {
    "GET /weather": RouteConfig(
        accepts=[
            PaymentOption(
                scheme="exact",
                pay_to=pay_to,
                price="$0.01",
                network="eip155:84532" # Base Sepolia
            )
        ],
        mime_type="application/json",
        description="Get weather"
    )
}

app.add_middleware(PaymentMiddlewareASGI, routes=routes, server=server)

@app.get("/")
async def get_root() -> dict[str, Any]:
    return {
        "home": {
        "root": "Payment Not Required"
        }
    }

@app.get("/weather")
async def get_weather() -> dict[str, Any]:
    return{
        "report": {
            "weather": "sunny",
            "temperature": 70
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4021)
    
