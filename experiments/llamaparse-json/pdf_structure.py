import nest_asyncio

nest_asyncio.apply()

from llama_parse import LlamaParse

parser = LlamaParse(
    api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
    result_type="json",
    varbose = True,
    language='en',
    num_workers=2
)

doc = parser.load_data(["input_document.pdf"])