import { Octokit } from "@octokit/rest";
import * as fs from "fs";
import * as path from "path";
import { getConfig } from "./config/index";

const config = getConfig();
const octokit = new Octokit({ auth: config.githubToken });

export async function createRepository(repoName: string) {
    try {
        const response = await octokit.rest.repos.createForAuthenticatedUser({
            name: repoName,
            private: true,
        });
        console.log(`Repository ${response.data.full_name} created successfully.`);
    } catch (error) {
        console.error(`Error creating repository: ${error}`);
    }
}

export async function uploadFile(repoName: string, filePath: string) {
    const content = fs.readFileSync(filePath, { encoding: "base64" });
    const fileName = path.basename(filePath);
    
    try {
        await octokit.rest.repos.createOrUpdateFileContents({
            owner: config.githubOwner,
            repo: repoName,
            path: fileName,
            message: `Upload ${fileName}`,
            content,
        });
        console.log(`File ${fileName} uploaded successfully.`);
    } catch (error) {
        console.error(`Error uploading file: ${error}`);
    }
}

export async function editFile(repoName: string, filePath: string, newContent: string) {
    const content = Buffer.from(newContent).toString("base64");
    const fileName = path.basename(filePath);
    
    try {
        const { data: { sha } } = await octokit.rest.repos.getContent({
            owner: config.githubOwner,
            repo: repoName,
            path: fileName,
        });

        await octokit.rest.repos.createOrUpdateFileContents({
            owner: config.githubOwner,
            repo: repoName,
            path: fileName,
            message: `Edit ${fileName}`,
            content,
            sha,
        });
        console.log(`File ${fileName} edited successfully.`);
    } catch (error) {
        console.error(`Error editing file: ${error}`);
    }
}