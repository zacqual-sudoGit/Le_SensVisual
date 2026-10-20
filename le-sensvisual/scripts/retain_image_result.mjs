/** Retain an actual tool result across a JS-to-file boundary.
 * No model/network calls, no CLI/shell interpolation, no private host imports.
 * Import from a file-capable Node host. Python production.py then saves/binds
 * supported image payloads. A full result is retained without printing pixels.
 */
import fs from 'node:fs/promises';
import path from 'node:path';

export async function retainImageResult(result, destination) {
  if (result == null) throw new Error('Retain the actual image result before leaving the generation call.');
  const text = JSON.stringify(result);
  if (!text || text === '{}' || text === '[]') throw new Error('Image result is empty; inspect the tool return contract.');
  const bytes = Buffer.from(text, 'utf8');
  if (bytes.length > 96 * 1024 * 1024) throw new Error('Result exceeds 96 MiB; use the supported host file-export route.');
  const file = path.resolve(destination);
  await fs.mkdir(path.dirname(file), { recursive: true });
  let handle;
  try {
    handle = await fs.open(file, 'wx');
  } catch (error) {
    if (error.code !== 'EEXIST') throw error;
    const existing = await fs.readFile(file);
    if (!existing.equals(bytes)) throw new Error('Result file already exists with different content; choose a new path.');
    return { result_file: file, bytes: bytes.length, unchanged: true };
  }
  try {
    await handle.writeFile(bytes);
  } catch (error) {
    await handle.close();
    await fs.unlink(file);
    throw error;
  }
  await handle.close();
  return { result_file: file, bytes: bytes.length };
}
