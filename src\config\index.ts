import dotenv from 'dotenv';

dotenv.config();

export const GITHUB_TOKEN = process.env.GITHUB_TOKEN || '';
export const GITHUB_USERNAME = process.env.GITHUB_USERNAME || '';
export const REPO_NAME = process.env.REPO_NAME || 'my-repo';
export const REPO_DESCRIPTION = process.env.REPO_DESCRIPTION || 'A project repository';
export const DEFAULT_BRANCH = process.env.DEFAULT_BRANCH || 'main';