import { Command } from 'commander';
import { uploadFiles, editFile } from './github';
import { loadConfig } from './config';
import { readFilesFromDirectory } from './utils';

const program = new Command();
const config = loadConfig();

program
  .name('github-uploader')
  .description('A command-line tool to upload and edit project folders on GitHub')
  .version('1.0.0');

program
  .command('upload <directory>')
  .description('Upload files from the specified directory to GitHub')
  .action(async (directory) => {
    try {
      const files = readFilesFromDirectory(directory);
      await uploadFiles(files, config);
      console.log('Files uploaded successfully!');
    } catch (error) {
      console.error('Error uploading files:', error);
    }
  });

program
  .command('edit <filePath> <content>')
  .description('Edit an existing file on GitHub')
  .action(async (filePath, content) => {
    try {
      await editFile(filePath, content, config);
      console.log('File edited successfully!');
    } catch (error) {
      console.error('Error editing file:', error);
    }
  });

program.parse(process.argv);