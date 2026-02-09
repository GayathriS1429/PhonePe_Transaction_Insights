repo_url = "https://github.com/PhonePe/pulse.git"
destination = "E:\PhonePe_Transaction_Insights\data"
from git import Repo
Repo.clone_from(repo_url, destination)