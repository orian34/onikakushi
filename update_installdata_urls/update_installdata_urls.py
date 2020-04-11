import re
import urllib.request


GITHUB_MASTER_BASE_URL = "https://raw.githubusercontent.com/07th-mod/python-patcher/master/"
INSTALL_DATA_URL = GITHUB_MASTER_BASE_URL + 'installData.json'

french_download_url_regex = re.compile('"https://github.com/orian34/(.*)/releases/download/[^"]+"', re.IGNORECASE)
latest_download_relative_path_regex = re.compile('"([^"]*/releases/download/[^"]*)"')


def get_url_as_text(url):
    with urllib.request.urlopen(url) as f:
        return f.read().decode('utf-8')


def get_file_from_release_url(github_latest_release_url: str):
    """
    Gets the URL of the first file attached to a release
    You can supply a 'latest' URL to get the latest release's artifact, eg:
    https://github.com/USER_NAME/REPO_NAME/releases/latest

    :returns The URL of the first file in the release, or None if no artifact is found
    """
    latest_download_page = get_url_as_text(github_latest_release_url)
    for line in latest_download_page.splitlines():
        match = latest_download_relative_path_regex.search(line)
        if match:
            return f'https://github.com{match.groups()[0]}'

    return None


def generate_updated_install_data():
    # download the latest installData.json from github
    install_data = get_url_as_text(INSTALL_DATA_URL)

    # Find and replace every french patch URL and replace it with the latest URL from each repo
    output_lines = []
    for line in install_data.splitlines():
        new_line = line

        match = french_download_url_regex.search(line)
        if match:
            repo_name = match.groups()[0]

            latest_release_url = f'https://github.com/orian34/{repo_name}/releases/latest'
            latest_artifact_url = get_file_from_release_url(latest_release_url)
            if latest_artifact_url is None:
                raise Exception(f"Couldn't find artifact at [{latest_release_url}] - are you sure there is a file attached?")

            new_line = french_download_url_regex.sub(f'"{latest_artifact_url}"', line)

            if new_line != line:
                print(f"Updated line:\n{line.strip()}\n{new_line.strip()}")
            else:
                print(f"No update required:\n{line.strip()}")

        output_lines.append(new_line + '\n')

    with open('installData.json', 'w', encoding='utf-8') as installDataOutput:
        installDataOutput.writelines(output_lines)


if __name__ == '__main__':
    generate_updated_install_data()
