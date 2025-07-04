from typing import Annotated, List, Optional
from langchain_core.tools import tool
from libs.utils.file import generate_unique_filename
from libs.utils.web import extract_webpage_contents, search_google as search_google_util
from libs.utils.web import (
    search_google_images,
    download_image as download_image_util,
)

@tool
def search_google(
    query: Annotated[str, "The search query to be used"],
) -> Annotated[
    List[dict],
    "A list of dictionaries containing the top search results with keys 'title', 'snippet', and 'link'",
]:
    """Searches Google for the specified query and returns the top search results"""
    return search_google_util(query)


@tool
def scrape_webpage(
    url: Annotated[str, "The URL of the webpage to scrape"],
    max_length: Annotated[Optional[int], "The maximum number of characters to return"],
) -> Annotated[str, "The important contents of the webpage"]:
    """Scrapes the specified webpage and returns its important contents"""
    return extract_webpage_contents(url, max_length) or "An error occurred. Try to use your own knowledge."

@tool
def google_image_search(
    query: Annotated[str, "The search query to be used"],
) -> Annotated[
    List[dict],
    "A list of dictionaries containing the top search results with keys 'title' and 'url'",
]:
    """Searches Google Images for the specified query and returns the top search results"""
    return search_google_images(query)


@tool
def download_image(
    image_url: Annotated[str, "The URL of the image to download"]
) -> Annotated[str, "The path where the image was saved"]:
    """Downloads the specified image from the URL to the specified path"""
    image_path = generate_unique_filename("image", "png", "imgs")
    return download_image_util(image_url, image_path)
