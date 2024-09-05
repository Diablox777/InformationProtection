import React, { useState } from "react";

const App = () => {
  const [data, setData] = useState<string>("");
  const [encryptedData, setEncryptedData] = useState<string>("");
  const [decryptedData, setDecryptedData] = useState<string>("");

  // Helper function for modular exponentiation
  const modPow = (base: bigint, exp: bigint, mod: bigint): bigint => {
    let result = 1n;
    base = base % mod;
    while (exp > 0) {
      if (exp % 2n === 1n) {
        result = (result * base) % mod;
      }
      exp = exp >> 1n;
      base = (base * base) % mod;
    }
    return result;
  };

  // Helper function for modular inverse using extended Euclidean algorithm
  const modInverse = (a: bigint, m: bigint): bigint => {
    let [m0, x0, x1] = [m, 0n, 1n];
    if (m === 1n) return 0n;

    while (a > 1n) {
      const q = a / m;
      [m, a] = [a % m, m];
      [x0, x1] = [x1 - q * x0, x0];
    }

    if (x1 < 0n) x1 += m0;
    return x1;
  };

  // Shamir's Secret Sharing Encryption/Decryption Example
  const shamirEncrypt = (data: string): string => {
    const p = 257n; // Prime number
    const c1 = 3n; // First private key
    const c2 = 5n; // Second private key

    // Encrypt each character
    const encrypted = Array.from(data).map((char) =>
      modPow(BigInt(char.charCodeAt(0)), c1 * c2, p).toString()
    );

    return encrypted.join(",");
  };

  const shamirDecrypt = (data: string): string => {
    const p = 257n;
    const c1 = 3n;
    const c2 = 5n;

    // Calculate modular inverse of c1 * c2 modulo (p-1)
    const inverse = modInverse(c1 * c2, p - 1n);

    // Decrypt each character
    const decrypted = data
      .split(",")
      .map((char) =>
        String.fromCharCode(
          Number(modPow(BigInt(char), inverse, p))
        )
      );

    return decrypted.join("");
  };

  // ElGamal Encryption/Decryption Example
  const elGamalEncrypt = (data: string): string => {
    const p = 257n;
    const g = 3n;
    const x = 5n;
    const y = modPow(g, x, p);

    const k = 7n; // Secret key
    const c1 = modPow(g, k, p);

    // Encrypt each character
    const encrypted = Array.from(data).map((char) => {
      const m = BigInt(char.charCodeAt(0));
      const c2 = (m * modPow(y, k, p)) % p;
      return `${c1},${c2}`;
    });

    return encrypted.join(";");
  };

  const elGamalDecrypt = (data: string): string => {
    const p = 257n;
    const x = 5n;

    // Decrypt each character
    const decrypted = data.split(";").map((pair) => {
      const [c1, c2] = pair.split(",").map(BigInt);
      const m = (c2 * modPow(c1, p - 1n - x, p)) % p;
      return String.fromCharCode(Number(m));
    });

    return decrypted.join("");
  };

  // Vernam Cipher (XOR Cipher) Encryption/Decryption Example
  const vernamEncrypt = (data: string): string => {
    const key = 42; // Simple XOR key
    const encrypted = Array.from(data).map(
      (char) => String.fromCharCode(char.charCodeAt(0) ^ key)
    );
    return encrypted.join("");
  };

  const vernamDecrypt = (data: string): string => {
    const key = 42; // Use the same key
    const decrypted = Array.from(data).map(
      (char) => String.fromCharCode(char.charCodeAt(0) ^ key)
    );
    return decrypted.join("");
  };

  // RSA Encryption/Decryption Example
  const rsaEncrypt = (data: string): string => {
    const p = 61n;
    const q = 53n;
    const n = p * q;
    const e = 17n;
    const encrypted = Array.from(data).map((char) =>
      modPow(BigInt(char.charCodeAt(0)), e, n).toString()
    );
    return encrypted.join(",");
  };

  const rsaDecrypt = (data: string): string => {
    const p = 61n;
    const q = 53n;
    const n = p * q;
    const e = 17n;
    const phi = (p - 1n) * (q - 1n);
    const d = modInverse(e, phi);

    const decrypted = data
      .split(",")
      .map((char) => String.fromCharCode(Number(modPow(BigInt(char), d, n))));

    return decrypted.join("");
  };

  // Handle file upload and processing
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      const file = event.target.files[0];
      const reader = new FileReader();
      reader.onload = () => {
        if (typeof reader.result === "string") {
          setData(reader.result);
        }
      };
      reader.readAsText(file);
    }
  };

  const handleFileDownload = (filename: string, content: string) => {
    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  };

  // Encrypt handler
  const handleEncrypt = (algorithm: string) => {
    let result = "";
    switch (algorithm) {
      case "shamir":
        result = shamirEncrypt(data);
        break;
      case "elgamal":
        result = elGamalEncrypt(data);
        break;
      case "vernam":
        result = vernamEncrypt(data);
        break;
      case "rsa":
        result = rsaEncrypt(data);
        break;
      default:
        result = data;
    }
    setEncryptedData(result);
  };

  // Decrypt handler
  const handleDecrypt = (algorithm: string) => {
    let result = "";
    switch (algorithm) {
      case "shamir":
        result = shamirDecrypt(encryptedData);
        break;
      case "elgamal":
        result = elGamalDecrypt(encryptedData);
        break;
      case "vernam":
        result = vernamDecrypt(encryptedData);
        break;
      case "rsa":
        result = rsaDecrypt(encryptedData);
        break;
      default:
        result = encryptedData;
    }
    setDecryptedData(result);
  };

  return (
    <div className="p-10 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">File Encryption</h1>

      <div className="mb-4">
        <input
          type="file"
          accept=".txt,.json,.csv,.xml" // Add any file types you need
          onChange={handleFileUpload}
        />
      </div>

      <textarea
        className="w-full p-2 border mb-4"
        rows={4}
        value={data}
        onChange={(e) => setData(e.target.value)}
        placeholder="Enter data to encrypt"
      />

      <div className="mb-4">
        <button
          className="bg-blue-500 text-white px-4 py-2 mr-2"
          onClick={() => handleEncrypt("shamir")}
        >
          Encrypt with Shamir
        </button>
        <button
          className="bg-blue-500 text-white px-4 py-2 mr-2"
          onClick={() => handleEncrypt("elgamal")}
        >
          Encrypt with ElGamal
        </button>
        <button
          className="bg-blue-500 text-white px-4 py-2 mr-2"
          onClick={() => handleEncrypt("vernam")}
        >
          Encrypt with Vernam
        </button>
        <button
          className="bg-blue-500 text-white px-4 py-2"
          onClick={() => handleEncrypt("rsa")}
        >
          Encrypt with RSA
        </button>
      </div>

      <textarea
        className="w-full p-2 border mb-4"
        rows={4}
        value={encryptedData}
        onChange={(e) => setEncryptedData(e.target.value)}
        placeholder="Encrypted data will appear here"
      />

      <div className="mb-4">
        <button
          className="bg-green-500 text-white px-4 py-2 mr-2"
          onClick={() => handleDecrypt("shamir")}
        >
          Decrypt with Shamir
        </button>
        <button
          className="bg-green-500 text-white px-4 py-2 mr-2"
          onClick={() => handleDecrypt("elgamal")}
        >
          Decrypt with ElGamal
        </button>
        <button
          className="bg-green-500 text-white px-4 py-2 mr-2"
          onClick={() => handleDecrypt("vernam")}
        >
          Decrypt with Vernam
        </button>
        <button
          className="bg-green-500 text-white px-4 py-2"
          onClick={() => handleDecrypt("rsa")}
        >
          Decrypt with RSA
        </button>
      </div>

      <textarea
        className="w-full p-2 border mb-4"
        rows={4}
        value={decryptedData}
        readOnly
        placeholder="Decrypted data will appear here"
      />

      <div className="mt-4">
        <button
          className="bg-gray-500 text-white px-4 py-2 mr-2"
          onClick={() => handleFileDownload("encrypted.txt", encryptedData)}
        >
          Download Encrypted File
        </button>
        <button
          className="bg-gray-500 text-white px-4 py-2"
          onClick={() => handleFileDownload("decrypted.txt", decryptedData)}
        >
          Download Decrypted File
        </button>
      </div>
    </div>
  );
};

export default App;
