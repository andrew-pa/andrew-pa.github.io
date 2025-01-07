"""
Static Blog Generator
=====================

Generates a static blog from Markdown files with YAML front matter.

- Uses Jinja2 templates
- Parses Markdown with front matter
- Embeds Open Graph and SEO meta tags
- Generates an RSS feed
- Optimizes images with Pillow
- Deploys via GitHub Actions
"""

import os
import sys
import glob
import shutil
import datetime
import calendar
import subprocess
from typing import Any, Dict, List, Tuple

import yaml
import markdown
from jinja2 import Environment, FileSystemLoader
from feedgen.feed import FeedGenerator
from PIL import Image

# Configuration & Utility Functions
# ------------------------------------------------------------------------------


def get_commit_hash() -> Tuple[str, str]:
    """
    Get the current commit hash (full and short) from the git repository.
    """
    try:
        full_hash = (
            subprocess.check_output(["git", "rev-parse", "HEAD"])
            .strip()
            .decode("utf-8")
        )
        short_hash = (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
            .strip()
            .decode("utf-8")
        )
        return full_hash, short_hash
    except subprocess.CalledProcessError:
        return "unknown", "unknown"


def load_config(config_file: str = "config.yml") -> Dict[str, Any]:
    """
    Load site-wide configuration from config.yml.
    """
    with open(config_file, "r", encoding="utf-8") as f:
        config: Dict[str, Any] = yaml.safe_load(f)
    config["current_date"] = datetime.datetime.now()
    config["production"] = "--prod" in sys.argv
    full_hash, short_hash = get_commit_hash()
    config["commit_hash"] = full_hash
    config["short_commit_hash"] = short_hash
    return config


def create_output_dirs() -> None:
    """
    Ensure required output directories exist (e.g., /output, /output/tags).
    """
    os.makedirs("output", exist_ok=True)
    os.makedirs("output/tags", exist_ok=True)
    os.makedirs("output/posts", exist_ok=True)
    os.makedirs("output/assets", exist_ok=True)


def slugify(value: str) -> str:
    """
    Create a URL-friendly slug from a string.
    Replaces non-alphanumeric characters with hyphens and lowercases everything.
    """
    return "".join(char if char.isalnum() else "-" for char in value.lower()).strip("-")


# ------------------------------------------------------------------------------
# Classes and Data Structures
# ------------------------------------------------------------------------------

from dataclasses import dataclass


@dataclass
class BlogPost:
    """
    Represents a blog post with associated metadata and content.
    """

    title: str
    pub_date: datetime.date
    tags: List[str]
    content: str  # HTML content
    summary: str
    slug: str
    year: int
    month: int
    media_files: List[str]

    @property
    def pub_date_str(self) -> str:
        """Return the publication date as a string."""
        return self.pub_date.strftime("%Y-%m-%d")

    @property
    def post_url(self) -> str:
        """Generate the expected relative URL for the post."""
        return f"posts/{self.year}/{self.month}/{self.slug}.html"


# ------------------------------------------------------------------------------
# Parsing and Post Collection
# ------------------------------------------------------------------------------


def parse_markdown_file(md_file_path: str) -> Tuple[Dict[str, Any], str]:
    """
    Parse a single Markdown file containing YAML front matter.
    Returns a tuple: (metadata_dict, md_content).
    """
    with open(md_file_path, "r", encoding="utf-8") as f:
        file_content = f.read()

    sections = file_content.split("---")
    if len(sections) < 3:
        raise ValueError(f"Invalid front matter in {md_file_path}")

    # Front matter is between the first pair of '---'
    front_matter_str = sections[1]
    body = "---".join(sections[2:])  # The rest is the Markdown body

    metadata: Dict[str, Any] = yaml.safe_load(front_matter_str)
    return metadata, body


def load_all_posts(posts_dir: str = "posts") -> List[BlogPost]:
    """
    Recursively load all posts from the /posts directory,
    returning a list of BlogPost objects.
    """
    all_posts: List[BlogPost] = []
    md_file_paths = glob.glob(os.path.join(posts_dir, "**", "post.md"), recursive=True)

    for md_file in md_file_paths:
        # Example path: posts/2024/my-post/post.md
        parts = md_file.split(os.sep)
        try:
            slug = parts[-2]
        except IndexError:
            continue  # Skip if path structure is unexpected
        print(f"Processing post {md_file}, slug={slug}")

        metadata, md_body = parse_markdown_file(md_file)

        # Convert the Markdown body to HTML
        html_content = markdown.markdown(md_body, output_format="html")

        # Parse publication date from metadata
        pub_date_str: str = metadata["pub_date"]
        pub_date: datetime.date = datetime.datetime.fromisoformat(pub_date_str)
        if pub_date.tzinfo is None:
            print(
                "Warning: publication date is not complete, missing time zone", pub_date
            )

        # Collect tags from metadata
        tags: List[str] = metadata.get("tags", [])

        # Identify media files in the same directory as post.md
        post_dir = os.path.dirname(md_file)
        media_files: List[str] = [
            f
            for f in os.listdir(post_dir)
            if os.path.isfile(os.path.join(post_dir, f))
            and f != "post.md"
            and not f.startswith("_")
        ]

        # Create BlogPost object
        post = BlogPost(
            title=metadata["title"],
            pub_date=pub_date,
            tags=tags,
            content=html_content,
            summary=metadata["summary"],
            slug=slug,
            year=pub_date.year,
            month=pub_date.month,
            media_files=media_files,
        )
        all_posts.append(post)

    # Sort descending by publication date
    all_posts.sort(key=lambda p: p.pub_date, reverse=True)
    return all_posts


# ------------------------------------------------------------------------------
# Template Rendering
# ------------------------------------------------------------------------------


def setup_jinja_env(templates_dir: str = "templates") -> Environment:
    """
    Setup Jinja2 environment to load templates from the specified directory.
    """
    env = Environment(loader=FileSystemLoader(templates_dir))
    env.filters["slugify"] = slugify
    return env


def render_home_page(
    env: Environment,
    config: Dict[str, Any],
    all_posts: List[BlogPost],
    all_tags: List[str],
) -> None:
    """
    Render the home page (index.html) listing recent posts.
    """
    print("Rendering home page")
    template = env.get_template("home.html")
    recent_posts = all_posts[: config["recent_posts_limit"]]

    rendered: str = template.render(
        config=config,
        page_title="Home",
        posts=recent_posts,
        tags=all_tags,
    )
    with open("output/index.html", "w", encoding="utf-8") as f:
        f.write(rendered)


def render_archive_page(
    env: Environment, config: Dict[str, Any], all_posts: List[BlogPost]
) -> None:
    """
    Render the archive page (archive.html) listing all posts grouped by year/month.
    """
    print("Rendering archive page")
    template = env.get_template("archive.html")

    # Group by year -> month
    archive_dict: Dict[str, Dict[str, List[BlogPost]]] = {}
    for post in all_posts:
        archive_dict.setdefault(str(post.year), {}).setdefault(
            calendar.month_name[post.month], []
        ).append(post)

    rendered: str = template.render(
        config=config,
        page_title="Archive",
        archive_dict=archive_dict,
    )
    with open("output/archive.html", "w", encoding="utf-8") as f:
        f.write(rendered)


def render_tag_pages(
    env: Environment,
    config: Dict[str, Any],
    all_posts_by_tag: Dict[str, List[BlogPost]],
) -> None:
    """
    Render a page for each unique tag, listing the relevant posts.
    """
    print("Rendering tag pages")
    template = env.get_template("tag.html")

    for tag, posts_with_tag in all_posts_by_tag.items():
        tag_slug = slugify(tag)
        output_path = os.path.join("output", "tags", f"{tag_slug}.html")

        rendered: str = template.render(
            config=config,
            page_title=tag,
            tag=tag,
            posts=posts_with_tag,
        )
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered)


def render_individual_posts(
    env: Environment, config: Dict[str, Any], all_posts: List[BlogPost]
) -> None:
    """
    Render individual post pages: /posts/<year>/<month>/<slug>.html
    """
    print("Rendering posts")
    template = env.get_template("post.html")
    for post in all_posts:
        post_output_dir = os.path.join(
            "output", "posts", str(post.year), str(post.month)
        )
        os.makedirs(post_output_dir, exist_ok=True)
        output_path = os.path.join(post_output_dir, f"{post.slug}.html")

        rendered: str = template.render(
            config=config,
            page_title=post.title,
            post=post,
            public_url=f"{config['base_url']}{post.post_url}",
        )
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered)


# ------------------------------------------------------------------------------
# RSS Feed Generation
# ------------------------------------------------------------------------------


def generate_rss_feed(config: Dict[str, Any], all_posts: List[BlogPost]) -> None:
    """
    Generate an RSS feed (feed.xml) listing all posts.
    """
    print("Generating RSS feed")
    fg = FeedGenerator()
    fg.title(config["site_title"])
    fg.link(href=config["base_url"], rel="alternate")
    fg.description(config.get("description", ""))
    fg.language("en")

    for post in all_posts:
        fe = fg.add_entry()
        fe.title(post.title)
        fe.link(href=f"{config['base_url']}{post.post_url}")
        fe.description(post.summary)
        fe.pubDate(post.pub_date)

    rss_path = "output/feed.xml"
    fg.rss_file(rss_path, pretty=True)
    print(f"RSS feed generated at {rss_path}")


# ------------------------------------------------------------------------------
# Assets Copy & Optimization
# ------------------------------------------------------------------------------


def copy_optimize_assets(
    public_dir: str = "public", output_assets_dir: str = "output/assets"
) -> None:
    """
    Copy and optimize all assets from public/ to output/assets/.
    Optimization example with Pillow for images (JPEG/PNG).
    """
    if not os.path.exists(public_dir):
        print(f"No public directory found at {public_dir}. Skipping asset copy.")
        return

    print("Copying assets from /public")

    for root, dirs, files in os.walk(public_dir):
        for file in files:
            src_path = os.path.join(root, file)
            rel_path = os.path.relpath(src_path, public_dir)
            dst_path = os.path.join(output_assets_dir, rel_path)

            os.makedirs(os.path.dirname(dst_path), exist_ok=True)

            # If file is an image, we optimize it
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                with Image.open(src_path) as img:
                    if file.lower().endswith(".png"):
                        img.save(dst_path, optimize=True)
                    else:
                        img.save(dst_path, optimize=True, quality=85)
            else:
                # For non-image files, just copy
                shutil.copy2(src_path, dst_path)

    print(f"Assets copied and optimized from {public_dir} to {output_assets_dir}.")


def copy_post_media(all_posts: List[BlogPost]) -> None:
    """
    Copy any media files (images, videos, etc.) associated with each post
    into the corresponding /output/posts/<year>/<month>/<slug>/ directory.
    Also performs basic optimization for images.
    """
    print("Copying post assets")
    for post in all_posts:
        source_dir = os.path.join("posts", str(post.year), str(post.month), post.slug)
        dest_dir = os.path.join(
            "output", "posts", str(post.year), str(post.month), post.slug
        )
        os.makedirs(dest_dir, exist_ok=True)

        for media_file in post.media_files:
            src_path = os.path.join(source_dir, media_file)
            dst_path = os.path.join(dest_dir, media_file)

            if not os.path.exists(src_path):
                continue

            if media_file.lower().endswith((".png", ".jpg", ".jpeg")):
                with Image.open(src_path) as img:
                    if media_file.lower().endswith(".png"):
                        img.save(dst_path, optimize=True)
                    else:
                        img.save(dst_path, optimize=True, quality=85)
            else:
                # For videos or other files
                shutil.copy2(src_path, dst_path)


# ------------------------------------------------------------------------------
# Main Generation Workflow
# ------------------------------------------------------------------------------


def main() -> None:
    """
    Main function to orchestrate the static site generation.
    """
    config = load_config("config.yml")
    print(yaml.dump(config))

    # 1. Ensure output directories exist
    create_output_dirs()

    # 2. Load all posts
    all_posts = load_all_posts("posts")
    all_posts_by_tag: Dict[str, List[BlogPost]] = {}

    for post in all_posts:
        for tag in post.tags:
            all_posts_by_tag.setdefault(tag, []).append(post)

    # 3. Setup Jinja environment
    env = setup_jinja_env("templates")

    # 4. Render pages
    render_home_page(env, config, all_posts, list(all_posts_by_tag.keys()))
    render_archive_page(env, config, all_posts)
    render_tag_pages(env, config, all_posts_by_tag)
    render_individual_posts(env, config, all_posts)

    # 5. Copy and optimize public assets
    copy_optimize_assets("public", "output/")

    # 6. Copy post media
    copy_post_media(all_posts)

    # 7. Generate RSS feed
    generate_rss_feed(config, all_posts)

    print("Static site generation completed successfully.")


if __name__ == "__main__":
    main()
