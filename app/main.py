import argparse
import json

from app.agents.agent import ResolutionAgent


def main():
    parser = argparse.ArgumentParser(description="Enterprise Production Resolution Agent")
    parser.add_argument("--order-id", type=int, default=5004, help="Order ID to investigate")
    parser.add_argument("--incident-id", default="INC-1001", help="Incident ID to associate with findings")
    parser.add_argument("--json", action="store_true", help="Print output as JSON")
    args = parser.parse_args()

    agent = ResolutionAgent()
    result = agent.run(order_id=args.order_id, incident_id=args.incident_id)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
        return

    print("Enterprise Production Resolution Agent")
    print("-" * 60)
    print(result["summary"])
    print("-" * 60)
    print(json.dumps(result["rca"], indent=2, default=str))


if __name__ == "__main__":
    main()