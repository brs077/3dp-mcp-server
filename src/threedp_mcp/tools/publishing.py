"""Publishing tools — GitHub Releases, Thingiverse, MyMiniFactory, Cults3D."""

import json
import os
import traceback
import urllib.request

from threedp_mcp.helpers import ensure_exported


def register(mcp, models: dict, output_dir: str):
    @mcp.tool()
    def publish_github_release(
        name: str,
        repo: str,
        tag: str,
        description: str = "",
        formats: str = '["stl", "step"]',
        draft: bool = False,
    ) -> str:
        """Publish a model to GitHub Releases.

        Uploads STL/STEP files as release assets. Requires the `gh` CLI to be
        installed and authenticated, OR a GITHUB_TOKEN environment variable.

        Args:
            name: Model name (must exist in current session)
            repo: GitHub repo in "owner/repo" format (e.g. "brs077/my-models")
            tag: Release tag (e.g. "v1.0.0" or "box-v1")
            description: Release description/notes
            formats: JSON list of formats to upload (default: ["stl", "step"])
            draft: If True, create as draft release
        """
        try:
            import shutil
            import subprocess

            fmt_list = json.loads(formats) if isinstance(formats, str) else formats

            # Export files
            files = []
            for fmt in fmt_list:
                path = ensure_exported(name, models, output_dir, fmt)
                files.append(path)

            # Check for gh CLI first (preferred)
            gh_path = shutil.which("gh")
            if gh_path:
                # Create release with gh CLI
                cmd = [
                    gh_path,
                    "release",
                    "create",
                    tag,
                    "--repo",
                    repo,
                    "--title",
                    f"{name} {tag}",
                    "--notes",
                    description or f"3D model: {name}",
                ]
                if draft:
                    cmd.append("--draft")
                cmd.extend(files)

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                if result.returncode != 0:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"gh release create failed: {result.stderr.strip()}",
                        },
                        indent=2,
                    )

                release_url = result.stdout.strip()
                return json.dumps(
                    {
                        "success": True,
                        "method": "gh_cli",
                        "release_url": release_url,
                        "tag": tag,
                        "repo": repo,
                        "files_uploaded": [os.path.basename(f) for f in files],
                    },
                    indent=2,
                )

            # Fallback: GitHub REST API with GITHUB_TOKEN
            token = os.environ.get("GITHUB_TOKEN", "")
            if not token:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Neither `gh` CLI nor GITHUB_TOKEN environment variable found. "
                        "Install gh (https://cli.github.com) or set GITHUB_TOKEN.",
                    },
                    indent=2,
                )

            import urllib.parse

            # Create release
            release_data = json.dumps(
                {
                    "tag_name": tag,
                    "name": f"{name} {tag}",
                    "body": description or f"3D model: {name}",
                    "draft": draft,
                }
            ).encode()

            req = urllib.request.Request(
                f"https://api.github.com/repos/{repo}/releases",
                data=release_data,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                release = json.loads(resp.read().decode())

            upload_url_template = release["upload_url"].replace("{?name,label}", "")
            uploaded = []

            # Upload each file as asset
            for filepath in files:
                filename = os.path.basename(filepath)
                content_type = "application/sla" if filename.endswith(".stl") else "application/octet-stream"

                with open(filepath, "rb") as f:
                    file_data = f.read()

                upload_url = f"{upload_url_template}?name={urllib.parse.quote(filename)}"
                req = urllib.request.Request(
                    upload_url,
                    data=file_data,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Accept": "application/vnd.github+json",
                        "Content-Type": content_type,
                    },
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=120) as resp:
                    asset = json.loads(resp.read().decode())
                    uploaded.append(asset.get("name", filename))

            return json.dumps(
                {
                    "success": True,
                    "method": "github_api",
                    "release_url": release.get("html_url", ""),
                    "tag": tag,
                    "repo": repo,
                    "files_uploaded": uploaded,
                },
                indent=2,
            )

        except Exception as e:
            return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)

    @mcp.tool()
    def publish_thingiverse(
        name: str,
        title: str,
        description: str = "",
        tags: str = '["3dprinting"]',
        category: str = "3D Printing",
        is_wip: bool = True,
    ) -> str:
        """Publish a model to Thingiverse.

        Creates a new Thing and uploads the STL file. Requires THINGIVERSE_TOKEN
        environment variable (OAuth access token).

        Get a token: https://www.thingiverse.com/developers → Create App → OAuth flow.

        Args:
            name: Model name (must exist in current session)
            title: Thing title on Thingiverse
            description: Thing description (supports markdown)
            tags: JSON list of tags (e.g. '["box", "organizer"]')
            category: Thingiverse category name
            is_wip: If True, publish as work-in-progress (default: True for safety)
        """
        try:
            token = os.environ.get("THINGIVERSE_TOKEN", "")
            if not token:
                return json.dumps(
                    {
                        "success": False,
                        "error": "THINGIVERSE_TOKEN environment variable not set. "
                        "Create an app at https://www.thingiverse.com/developers "
                        "and complete OAuth to get an access token.",
                    },
                    indent=2,
                )

            stl_path = ensure_exported(name, models, output_dir, "stl")
            tag_list = json.loads(tags) if isinstance(tags, str) else tags

            # Step 1: Create the Thing
            thing_data = json.dumps(
                {
                    "name": title,
                    "description": description or f"3D-printable model: {title}",
                    "tags": tag_list,
                    "category": category,
                    "is_wip": is_wip,
                }
            ).encode()

            req = urllib.request.Request(
                "https://api.thingiverse.com/things",
                data=thing_data,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                thing = json.loads(resp.read().decode())

            thing_id = thing.get("id")
            if not thing_id:
                return json.dumps(
                    {"success": False, "error": "Failed to create Thing — no ID returned", "response": thing}, indent=2
                )

            # Step 2: Upload the STL file
            filename = os.path.basename(stl_path)
            file_req_data = json.dumps({"filename": filename}).encode()

            req = urllib.request.Request(
                f"https://api.thingiverse.com/things/{thing_id}/files",
                data=file_req_data,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                upload_info = json.loads(resp.read().decode())

            # Thingiverse returns S3 upload fields — perform multipart upload
            s3_action = upload_info.get("action", "")
            s3_fields = upload_info.get("fields", {})

            if s3_action and s3_fields:
                import io

                boundary = "----3dpMcpBoundary"
                body = io.BytesIO()

                for key, value in s3_fields.items():
                    body.write(f"--{boundary}\r\n".encode())
                    body.write(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode())
                    body.write(f"{value}\r\n".encode())

                # Add file
                with open(stl_path, "rb") as f:
                    file_data = f.read()
                body.write(f"--{boundary}\r\n".encode())
                body.write(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode())
                body.write(b"Content-Type: application/sla\r\n\r\n")
                body.write(file_data)
                body.write(b"\r\n")
                body.write(f"--{boundary}--\r\n".encode())

                req = urllib.request.Request(
                    s3_action,
                    data=body.getvalue(),
                    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=120) as resp:
                    pass  # S3 returns 204 on success

                # Step 3: Finalize the upload
                finalize_url = upload_info.get(
                    "finalize_url",
                    f"https://api.thingiverse.com/things/{thing_id}/files/{upload_info.get('id', '')}/finalize",
                )
                req = urllib.request.Request(
                    finalize_url,
                    headers={"Authorization": f"Bearer {token}"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    pass

            thing_url = thing.get("public_url", f"https://www.thingiverse.com/thing:{thing_id}")
            return json.dumps(
                {
                    "success": True,
                    "thing_id": thing_id,
                    "thing_url": thing_url,
                    "title": title,
                    "file_uploaded": filename,
                    "is_wip": is_wip,
                    "note": "Published as WIP. Edit on Thingiverse to add images and finalize." if is_wip else "",
                },
                indent=2,
            )

        except Exception as e:
            return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)

    @mcp.tool()
    def publish_myminifactory(
        name: str,
        title: str,
        description: str = "",
        tags: str = '["3dprinting"]',
        category_id: int = 0,
    ) -> str:
        """Publish a model to MyMiniFactory.

        Creates a new object and uploads the STL file via 3-step API. Requires
        MYMINIFACTORY_TOKEN environment variable (OAuth access token).

        Get credentials: https://www.myminifactory.com/api-documentation

        Args:
            name: Model name (must exist in current session)
            title: Object title on MyMiniFactory
            description: Object description
            tags: JSON list of tags
            category_id: MyMiniFactory category ID (0 = uncategorized)
        """
        try:
            token = os.environ.get("MYMINIFACTORY_TOKEN", "")
            if not token:
                return json.dumps(
                    {
                        "success": False,
                        "error": "MYMINIFACTORY_TOKEN environment variable not set. "
                        "Register at https://www.myminifactory.com/api-documentation for API access.",
                    },
                    indent=2,
                )

            stl_path = ensure_exported(name, models, output_dir, "stl")
            tag_list = json.loads(tags) if isinstance(tags, str) else tags

            # Step 1: Create the object
            object_data = json.dumps(
                {
                    "name": title,
                    "description": description or f"3D-printable model: {title}",
                    "tags": tag_list,
                    "visibility": "draft",
                }
            ).encode()

            req = urllib.request.Request(
                "https://www.myminifactory.com/api/v2/objects",
                data=object_data,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                obj = json.loads(resp.read().decode())

            object_id = obj.get("id")
            if not object_id:
                return json.dumps({"success": False, "error": "Failed to create object", "response": obj}, indent=2)

            # Step 2: Upload the STL file
            filename = os.path.basename(stl_path)
            with open(stl_path, "rb") as f:
                file_data = f.read()

            boundary = "----3dpMcpBoundary"
            body = b""
            body += f"--{boundary}\r\n".encode()
            body += f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode()
            body += b"Content-Type: application/sla\r\n\r\n"
            body += file_data
            body += b"\r\n"
            body += f"--{boundary}--\r\n".encode()

            req = urllib.request.Request(
                f"https://www.myminifactory.com/api/v2/objects/{object_id}/files",
                data=body,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": f"multipart/form-data; boundary={boundary}",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                json.loads(resp.read().decode())

            object_url = obj.get("url", f"https://www.myminifactory.com/object/3d-print-{object_id}")
            return json.dumps(
                {
                    "success": True,
                    "object_id": object_id,
                    "object_url": object_url,
                    "title": title,
                    "file_uploaded": filename,
                    "status": "draft",
                    "note": "Published as draft. Visit MyMiniFactory to add images, set category, and publish.",
                },
                indent=2,
            )

        except Exception as e:
            return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)

    @mcp.tool()
    def publish_cults3d(
        name: str,
        title: str,
        description: str = "",
        tags: str = '["3dprinting"]',
        license: str = "creative_commons_attribution",
        free: bool = True,
        price_cents: int = 0,
    ) -> str:
        """Publish a model to Cults3D via their GraphQL API.

        Creates a new creation with metadata. NOTE: Cults3D requires files to be
        hosted at a URL — the STL is uploaded to a file hosting service or the user
        provides a URL. For simplicity, this tool creates the listing and provides
        instructions for manual file upload.

        Requires CULTS3D_API_KEY environment variable (API key from profile settings).

        Args:
            name: Model name (must exist in current session)
            title: Creation title on Cults3D
            description: Creation description (HTML allowed)
            tags: JSON list of tags
            license: License type (e.g. "creative_commons_attribution")
            free: If True, publish as free model
            price_cents: Price in cents (only used if free=False)
        """
        try:
            import base64

            api_key = os.environ.get("CULTS3D_API_KEY", "")
            if not api_key:
                return json.dumps(
                    {
                        "success": False,
                        "error": "CULTS3D_API_KEY environment variable not set. "
                        "Get your API key from https://cults3d.com/en/pages/api",
                    },
                    indent=2,
                )

            stl_path = ensure_exported(name, models, output_dir, "stl")
            tag_list = json.loads(tags) if isinstance(tags, str) else tags

            # Cults3D uses GraphQL with Basic Auth (api_key as username, empty password)
            auth_str = base64.b64encode(f"{api_key}:".encode()).decode()

            # GraphQL mutation to create a creation
            query = """
        mutation CreateCreation($input: CreationInput!) {
            createCreation(input: $input) {
                creation {
                    id
                    slug
                    url
                }
                errors
            }
        }
        """

            variables = {
                "input": {
                    "name": title,
                    "description": description or f"3D-printable model: {title}",
                    "tags": tag_list,
                    "license": license,
                    "free": free,
                    "price": price_cents if not free else 0,
                    "status": "draft",
                }
            }

            graphql_data = json.dumps({"query": query, "variables": variables}).encode()

            req = urllib.request.Request(
                "https://cults3d.com/graphql",
                data=graphql_data,
                headers={
                    "Authorization": f"Basic {auth_str}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())

            creation_data = result.get("data", {}).get("createCreation", {})
            errors = creation_data.get("errors", [])
            creation = creation_data.get("creation", {})

            if errors:
                return json.dumps({"success": False, "errors": errors}, indent=2)

            return json.dumps(
                {
                    "success": True,
                    "creation_id": creation.get("id"),
                    "creation_url": creation.get("url", ""),
                    "slug": creation.get("slug", ""),
                    "title": title,
                    "status": "draft",
                    "stl_path": stl_path,
                    "note": "Created as draft. Cults3D requires file upload through their web interface "
                    "or hosting files at a public URL. Upload the STL file manually at the creation URL.",
                },
                indent=2,
            )

        except Exception as e:
            return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)
