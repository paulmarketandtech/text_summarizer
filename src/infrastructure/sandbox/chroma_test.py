import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import chromadb

    return (chromadb,)


@app.cell(hide_code=True)
def dummy_texts():
    amd_summary="""
    KPIs & Financial Metrics:

    bullet points...
    Investment Thesis:

    Bull Case: The potential for significant performance improvements in AI processing could drive strong growth and market share gains.
    Bear Case: There is a risk that chips may be tied to specific models, limiting flexibility.
    Specific Strengths:

    Potential for significant performance improvements in AI processing
    Specific Weaknesses:

    Risk of chips being tied to specific models, limiting flexibility
    Key Catalysts:

    Acquisition of Talis and its integration with AMD's existing solutions
    """
    nvidia_summary = """
    KPIs & Financial Metrics:

    bullet points...
    Investment Thesis:

    Bull Case: Continued growth in AI spending by major tech companies, leading position in the AI chip market, and expected continued growth in AI spending.
    Bear Case: High capital expenditure budgets leading to negative free cash flow, reliance on borrowing and issuing new shares for funding, uncertain useful lifespan of GPUs, and potential slowing down of AI spending.
    Specific Strengths:

    Leading position in AI chip market
    Significant growth in AI spending by major tech companies
    Betting on GPU as an asset class
    Expected continued growth in AI spending
    Key Catalysts:

    Continued growth in AI spending by hyperscalers
    AMD's acquisition plans to improve memory efficiency
    Earnings report on August 26th
    """
    fried_chicken = """
    A classic Southern fried chicken recipe involves marinating cut-up chicken in buttermilk and spices, then coating it in a seasoned flour mixture before frying.  For an extra crispy crust, many chefs recommend a double-dredge technique or adding cornstarch to the flour blend. 

    Key techniques for success include:

    Marination: Soak chicken in buttermilk (optionally with hot sauce) for at least 2 hours or overnight to ensure juiciness and tenderness. 
    Coating: Dredge the chicken in a mixture of all-purpose flour, cornstarch, paprika, garlic powder, onion powder, salt, and black pepper. 
    Frying: Heat vegetable oil to 340–350°F (170–175°C) in a Dutch oven or deep skillet.  Fry in batches to avoid overcrowding, cooking until the internal temperature reaches 165°F (74°C) and the crust is golden brown. 
    Resting: Let the chicken rest on a wire rack rather than paper towels to maintain crust crispiness. 
    Variations include Korean fried chicken (tossed in a sweet and spicy gochujang sauce) or Indian fried chicken (marinated in yogurt, ginger-garlic paste, and spices like garam masala and cumin). For those without buttermilk, a mixture of milk and lemon juice or vinegar can serve as a substitute for the marinade.
    """
    apple_pie = """
    For a classic, foolproof homemade apple pie, combine 3 pounds of tart apples (such as Granny Smith or Honeycrisp) with 1/2 to 2/3 cup sugar, 3 tablespoons flour, 1/2 teaspoon cinnamon, 1/4 teaspoon nutmeg, and 1 teaspoon vanilla.  Toss the sliced apples with 1 tablespoon lemon juice to prevent browning, then fill a double crust (all-butter or sour cream dough) and bake at 425°F for 15 minutes, then reduce to 375°F for 45–60 minutes until golden and bubbly. 

    Key Variations & Tips
    No-Precook Method: Most recipes, like those from Sugar Spun Run and Simply Recipes, recommend raw filling for better texture; however, macerating apples for 45 minutes helps draw out excess moisture to prevent a soggy crust. 
    Thickening Agents: While flour is traditional, tapioca starch (Serious Eats) or cornstarch can be used for a clearer, thicker gel.
    Crust: Use a double crust for a traditional pie, or a lattice top for visual appeal and better steam release. 
    Apples: Mix tart and sweet varieties (e.g., Granny Smith with Fuji or Jonagold) for complex flavor and structural integrity during baking.
    """
    return (nvidia_summary,)


@app.cell
def _(chromadb, nvidia_summary):
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction  # or Nomic / SentenceTransformer

    client = chromadb.HttpClient(host="192.168.0.164", port=8000)
    print(client.heartbeat())  # should return a number

    # Use default
    collection = client.get_or_create_collection("testing")

    # Or with custom EF
    # collection = client.get_or_create_collection("test", embedding_function=your_ef)

    collection.add(
        documents=nvidia_summary,
        ids=["doc4"]
    )
    return (collection,)


@app.cell
def _(collection):
    results = collection.query(query_texts=["i want to invest money"], n_results=2)
    print(results)
    return (results,)


@app.cell
def _(results):
    for k, v in results.items():
        if k == "documents":
            print(v[0][1])
    return


@app.cell
def _():
    from dotenv import load_dotenv

    load_dotenv()
    from src.rag.retriever import DataRetriever
    from src.storage.database import get_session
    from src.storage.vector_db import VectorDBManager

    vector_db = VectorDBManager("../../../data/chromadb/")
    with get_session() as session:
        retriever = DataRetriever(session, vector_db)
        r = retriever.search_for_chunk("i Want to invest money", 2)
        #print(r)
        for chunk in r["relevant_chunks"]:
            print(chunk)
            print("=" * 40)
    return


@app.cell
def _():
    """
    steps to be implemented:
    1 user provides url:
    - both (more like prod): watcher/observer?

    2 checks if video already processed
    - both (more like prod): extracts the id from url
    - prod: checks if id in db
    - dev: skip for now

    2a is in db then display summary. if not in db go to 3

    ====IMPLEMENT THIS=====
    3 getting trascript
    - prod: real url, connects to api and downloads the transcript
    - dev: reads local saved transcript

    4 chunking text
    - both: uses chunker

    5 extract data from each chunk
    - both: data extractor

    6 creating summary for each stock and whole report
    - both: text summarizer

    =====AND THIS=======
    7 manage output
    - prod: file manager
    - dev: print or save to local file - no need for abstract implementation

    EXTRA feature for now
    connecting to vector db.
    - prod: connects to lxc client
    - dev: ???? embed remotly, save locally?
    """
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
