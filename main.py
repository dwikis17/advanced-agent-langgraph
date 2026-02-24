from dotenv import load_dotenv
result = load_dotenv()
print("Dotenv loaded:", result)  # Should print True if .env was found

from src.workflow import Workflow  # Now imports happen after env is loaded
import os

print("API Key:", os.getenv("FIRE_CRAWL_API_KEY"))

def main():
    workflow = Workflow()
    print("Welcome advanced Agent !")

    while True:
        query = input("\nDeveloper Tools: ")
        if query == "quit":
            break

        if query:
            result = workflow.run(query)
            print(f"Result: for {query}")
            print("-" * 60)

            for i, company in enumerate(result.companies, 1):
                print(f"\n{i} {company.name}")
                print(f"   {company.description}")

            if result.analysis:
                print(f"Analysis Recommendations: {result.analysis}")

if __name__ == "__main__":
    main()