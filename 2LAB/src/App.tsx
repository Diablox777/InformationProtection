import React, { useState } from "react";

const App = () => {
  const [data, setData] = useState<string>("");
  const [encryptedData, setEncryptedData] = useState<string>("");
  const [decryptedData, setDecryptedData] = useState<string>("");
  const [useRandomKeys, setUseRandomKeys] = useState<boolean>(false);

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

  // Generate random BigInt within a range
  const randomBigInt = (min: number, max: number): bigint => {
    return BigInt(Math.floor(Math.random() * (max - min + 1)) + min);
  };

  // Shamir's Secret Sharing Encryption/Decryption Example
  const shamirEncrypt = (data: string): string => {
    const p = useRandomKeys ? randomBigInt(257, 1021) : 257n; // Prime number
    const c1 = useRandomKeys ? randomBigInt(2, 50) : 3n; // First private key
    const c2 = useRandomKeys ? randomBigInt(2, 50) : 5n; // Second private key

    // Encrypt each character
    const encrypted = Array.from(data).map((char) =>
      modPow(BigInt(char.charCodeAt(0)), c1 * c2, p).toString()
    );

    return encrypted.join(",");
  };

  const shamirDecrypt = (data: string): string => {
    const p = useRandomKeys ? randomBigInt(257, 1021) : 257n;
    const c1 = useRandomKeys ? randomBigInt(2, 50) : 3n;
    const c2 = useRandomKeys ? randomBigInt(2, 50) : 5n;

    // Calculate modular inverse of c1 * c2 modulo (p-1)
    const inverse = modInverse(c1 * c2, p - 1n);

    // Decrypt each character
    const decrypted = data
      .split(",")
      .map((char) =>
        String.fromCharCode(Number(modPow(BigInt(char), inverse, p)))
      );

    return decrypted.join("");
  };

  // ElGamal Encryption/Decryption Example
  const elGamalEncrypt = (data: string): string => {
    const p = useRandomKeys ? randomBigInt(257, 1021) : 257n;
    const g = useRandomKeys ? randomBigInt(2, 100) : 3n;
    const x = useRandomKeys ? randomBigInt(2, 100) : 5n;
    const y = modPow(g, x, p);

    const k = useRandomKeys ? randomBigInt(2, 100) : 7n; // Secret key
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
    const p = useRandomKeys ? randomBigInt(257, 1021) : 257n;
    const x = useRandomKeys ? randomBigInt(2, 100) : 5n;

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
    const key = useRandomKeys ? Math.floor(Math.random() * 256) : 42; // Simple XOR key
    const encrypted = Array.from(data).map((char) =>
      String.fromCharCode(char.charCodeAt(0) ^ key)
    );
    return encrypted.join("");
  };

  const vernamDecrypt = (data: string): string => {
    const key = useRandomKeys ? Math.floor(Math.random() * 256) : 42; // Use the same key
    const decrypted = Array.from(data).map((char) =>
      String.fromCharCode(char.charCodeAt(0) ^ key)
    );
    return decrypted.join("");
  };

  // RSA Encryption/Decryption Example
  const rsaEncrypt = (data: string): string => {
    const p = useRandomKeys ? randomBigInt(61, 101) : 61n;
    const q = useRandomKeys ? randomBigInt(53, 103) : 53n;
    const n = p * q;
    const e = 17n;
    const encrypted = Array.from(data).map((char) =>
      modPow(BigInt(char.charCodeAt(0)), e, n).toString()
    );
    return encrypted.join(",");
  };

  const rsaDecrypt = (data: string): string => {
    const p = useRandomKeys ? randomBigInt(61, 101) : 61n;
    const q = useRandomKeys ? randomBigInt(53, 103) : 53n;
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

  // Toggle between fixed and random keys
  const toggleKeyType = () => {
    setUseRandomKeys((prev) => !prev);
  };

  return (
    <div className="container mx-auto p-10 max-w-[1100px]">
      <h1 className="text-2xl font-bold mb-5">Encryption and Decryption</h1>

      <input
        type="file"
        onChange={handleFileUpload}
        className="mb-5"
      />
      <textarea
        value={data}
        onChange={(e) => setData(e.target.value)}
        rows={5}
        className="w-full p-2 mb-5 border border-gray-300"
        placeholder="Enter text or upload a file"
      />

      <div className="mb-5">
        <button
          onClick={toggleKeyType}
          className="bg-blue-500 text-white py-2 px-4 rounded mb-5"
        >
          {useRandomKeys ? "Switch to Fixed Keys" : "Switch to Random Keys"}
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <button
          onClick={() => handleEncrypt("shamir")}
          className="bg-green-500 text-white py-2 px-4 rounded"
        >
          Encrypt (Shamir)
        </button>
        <button
          onClick={() => handleDecrypt("shamir")}
          className="bg-red-500 text-white py-2 px-4 rounded"
        >
          Decrypt (Shamir)
        </button>
        <button
          onClick={() => handleEncrypt("elgamal")}
          className="bg-green-500 text-white py-2 px-4 rounded"
        >
          Encrypt (ElGamal)
        </button>
        <button
          onClick={() => handleDecrypt("elgamal")}
          className="bg-red-500 text-white py-2 px-4 rounded"
        >
          Decrypt (ElGamal)
        </button>
        <button
          onClick={() => handleEncrypt("vernam")}
          className="bg-green-500 text-white py-2 px-4 rounded"
        >
          Encrypt (Vernam)
        </button>
        <button
          onClick={() => handleDecrypt("vernam")}
          className="bg-red-500 text-white py-2 px-4 rounded"
        >
          Decrypt (Vernam)
        </button>
        <button
          onClick={() => handleEncrypt("rsa")}
          className="bg-green-500 text-white py-2 px-4 rounded"
        >
          Encrypt (RSA)
        </button>
        <button
          onClick={() => handleDecrypt("rsa")}
          className="bg-red-500 text-white py-2 px-4 rounded"
        >
          Decrypt (RSA)
        </button>
      </div>

      <div className="mt-5">
        <h2 className="text-xl font-bold mb-2">Encrypted Data:</h2>
        <textarea
          value={encryptedData}
          readOnly
          rows={5}
          className="w-full p-2 mb-5 border border-gray-300"
        />

        <h2 className="text-xl font-bold mb-2">Decrypted Data:</h2>
        <textarea
          value={decryptedData}
          readOnly
          rows={5}
          className="w-full p-2 border border-gray-300"
        />

        <div className="mt-5">
          <button
            onClick={() => handleFileDownload("encrypted.txt", encryptedData)}
            className="bg-blue-500 text-white py-2 px-4 rounded"
          >
            Download Encrypted Data
          </button>
        </div>
      </div>
    </div>
  );
};

export default App;
