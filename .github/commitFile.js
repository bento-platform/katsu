async function getFileSha(fileName, github_ref, octokit, context) {
  const path = "chord_metadata_service/mohpackets/docs/" + fileName;
  const { data } = await octokit.repos.getContent({
    owner: context.repo.owner,
    repo: context.repo.repo,
    path,
    ref: github_ref,
  });
  return data.sha;
}

async function commitAndPushChanges(
  fileName,
  github_ref,
  fs,
  octokit,
  context
) {
  const repoPath = "chord_metadata_service/mohpackets/docs/";
  const fileSha = await getFileSha(fileName, github_ref, octokit, context);

  // Read the content of the updated file
  const fileContent = fs.readFileSync(`./${repoPath}${fileName}`, "utf8");

  // Commit and push changes
  await octokit.request(
    `PUT /repos/{owner}/{repo}/contents/${repoPath}{fileName}`,
    {
      owner: context.repo.owner,
      repo: context.repo.repo,
      fileName,
      message: `Update ${fileName}`,
      content: Buffer.from(fileContent).toString("base64"),
      sha: fileSha,
      branch: github_ref,
    }
  );
}

module.exports = {
  commitAndPushChanges,
};
