// catchError.js
export async function catchError(promise) {
    try {
      const data = await promise;
      return [null, data];
    } catch (error) {
      return [error, null];
    }
  }
  