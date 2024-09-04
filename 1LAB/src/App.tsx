import React, { useState } from 'react';
import './App.css';

const App: React.FC = () => {
  // State для быстрой экспоненциации
  const [base, setBase] = useState<number>(0);
  const [exponent, setExponent] = useState<number>(0);
  const [modulus, setModulus] = useState<number>(1);
  const [modExpResult, setModExpResult] = useState<number | null>(null);

  // State для расширенного алгоритма Евклида
  const [a, setA] = useState<number>(0);
  const [b, setB] = useState<number>(0);
  const [gcdResult, setGcdResult] = useState<[number, number, number] | null>(null);

  // State для Диффи-Хеллмана
  const [p, setP] = useState<number>(0);
  const [g, setG] = useState<number>(0);
  const [privateA, setPrivateA] = useState<number>(0);
  const [privateB, setPrivateB] = useState<number>(0);
  const [sharedKey, setSharedKey] = useState<number | null>(null);

  // State для алгоритма "Шаг младенца, шаг великана"
  const [g2, setG2] = useState<number>(0);
  const [h, setH] = useState<number>(0);
  const [p2, setP2] = useState<number>(0);
  const [logResult, setLogResult] = useState<number | null>(null);

  // Функция быстрого возведения в степень по модулю
  const modExp = (base: number, exponent: number, modulus: number): number => {
    if (modulus === 1) return 0;
    
    let result = 1;
    base = ((base % modulus) + modulus) % modulus;  // Убедимся, что base неотрицательный
  
    while (exponent > 0) {
      if (exponent % 2 === 1) {
        result = (result * base) % modulus;  // Промежуточное умножение, взятое по модулю
      }
      base = (base * base) % modulus;  // Промежуточное возведение в квадрат, взятое по модулю
      exponent = Math.floor(exponent / 2);  // Снижаем степень вдвое
    }
    
    return result;
  };

  // Функция расширенного алгоритма Евклида
  const extendedGCD = (a: number, b: number): [number, number, number] => {
    if (b === 0) {
      return [Math.abs(a), Math.sign(a), 0]; // Возвращаем модуль a и корректные коэффициенты
    }
  
    const [gcd, x1, y1] = extendedGCD(b, a % b);
    const x = y1;
    const y = x1 - Math.floor(a / b) * y1;
    return [gcd, x, y];
  };

  // Функция Диффи-Хеллмана для генерации общего ключа
  const diffieHellman = (p: number, g: number, a: number, b: number): number => {
    const A = modExp(g, a, p);
    const B = modExp(g, b, p);
    const sharedKey = modExp(B, a, p);
    return sharedKey;
  };

  // Алгоритм «Шаг младенца, шаг великана»
  const babyStepGiantStep = (g: number, h: number, p: number): number | null => {
    const m = Math.ceil(Math.sqrt(p));
    const valueMap = new Map<number, number>();
  
    // Этап шага младенца
    for (let j = 0; j < m; j++) {
      const modValue = modExp(g, j, p);
      if (!valueMap.has(modValue)) {
        valueMap.set(modValue, j);
      }
    }
  
    // Вычисление g^(-m) mod p
    const gInvM = modExp(g, p - 1 - m, p);
  
    // Этап шага великана
    for (let i = 0; i < m; i++) {
      const y = (h * modExp(gInvM, i, p)) % p;
      if (valueMap.has(y)) {
        return i * m + valueMap.get(y)!;
      }
    }
    return null; // Если не найден логарифм
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8 flex flex-col items-center justify-center">
      <h1 className="text-3xl font-bold mb-6 text-center">Криптографическая библиотека</h1>
  
      {/* Блок для быстрой экспоненциации */}
      <div className="bg-white shadow-lg rounded-lg p-6 mb-6 w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">Модульное возведение в степень</h2>
        <input
          type="number"
          placeholder="Основание"
          value={base}
          onChange={(e) => setBase(Number(e.target.value))}
          className="block w-full mb-2 p-2 border rounded"
        />
        <input
          type="number"
          placeholder="Показатель степени"
          value={exponent}
          onChange={(e) => setExponent(Number(e.target.value))}
          className="block w-full mb-2 p-2 border rounded"
        />
        <input
          type="number"
          placeholder="Модуль"
          value={modulus}
          onChange={(e) => setModulus(Number(e.target.value))}
          className="block w-full mb-2 p-2 border rounded"
        />
        <button
          onClick={() => setModExpResult(modExp(base, exponent, modulus))}
          className="bg-blue-500 text-white px-4 py-2 rounded mt-2"
        >
          Вычислить
        </button>
        {modExpResult !== null && (
          <div className="mt-4">
            <strong>Результат:</strong> {modExpResult} <br />
            <p>Это результат возведения {base} в степень {exponent} по модулю {modulus}.</p>
          </div>
        )}
      </div>
  
      {/* Блок для расширенного алгоритма Евклида */}
      <div className="bg-white shadow-lg rounded-lg p-6 mb-6 w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">Расширенный алгоритм Евклида</h2>
        <input
          type="number"
          placeholder="a"
          value={a}
          onChange={(e) => setA(Number(e.target.value))}
          className="block w-full mb-2 p-2 border rounded"
        />
        <input
          type="number"
          placeholder="b"
          value={b}
          onChange={(e) => setB(Number(e.target.value))}
          className="block w-full mb-2 p-2 border rounded"
        />
        <button
          onClick={() => setGcdResult(extendedGCD(a, b))}
          className="bg-blue-500 text-white px-4 py-2 rounded mt-2"
        >
          Вычислить НОД
        </button>
        {gcdResult && (
          <div className="mt-4">
            <strong>НОД:</strong> {gcdResult[0]} <br />
            <strong>x:</strong> {gcdResult[1]} <br />
            <strong>y:</strong> {gcdResult[2]} <br />
            <p>НОД ({a}, {b}) равен {gcdResult[0]}. Коэффициенты x и y такие, что {a}*{gcdResult[1]} + {b}*{gcdResult[2]} = {gcdResult[0]}.</p>
          </div>
        )}
      </div>
  
      {/* Блок для Диффи-Хеллмана */}
      <div className="bg-white shadow-lg rounded-lg p-6 mb-6 w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">Обмен ключами Диффи-Хеллмана</h2>
        <input
          type="number"
          placeholder="Простое число p"
          value={p}
          onChange={(e) => setP(Number(e.target.value))}
          className="block w-full mb-2 p-2 border rounded"
        />
        <input
          type="number"
          placeholder="Генератор g"
          value={g}
          onChange={(e) => setG(Number(e.target.value))}
          className="block w-full mb-2 p-2 border rounded"
        />
        <input
          type="number"
          placeholder="Приватный ключ A"
          value={privateA}
          onChange={(e) => setPrivateA(Number(e.target.value))}
          className="block w-full mb-2 p-2 border rounded"
        />
        <input
          type="number"
          placeholder="Приватный ключ B"
          value={privateB}
          onChange={(e) => setPrivateB(Number(e.target.value))}
          className="block w-full mb-2 p-2 border rounded"
        />
        <button
          onClick={() => setSharedKey(diffieHellman(p, g, privateA, privateB))}
          className="bg-blue-500 text-white px-4 py-2 rounded mt-2"
        >
          Вычислить общий ключ
        </button>
        {sharedKey !== null && (
          <div className="mt-4">
            <strong>Общий ключ:</strong> {sharedKey} <br />
            <p>Этот ключ является результатом обмена ключами между A и B с использованием простого числа {p} и генератора {g}.</p>
          </div>
        )}
      </div>
  
      {/* Блок для алгоритма "Шаг младенца, шаг великана" */}
      <div className="bg-white shadow-lg rounded-lg p-6 mb-6 w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">Алгоритм "Шаг младенца, шаг великана"</h2>
        <input
          type="number"
          placeholder="g"
          value={g2}
          onChange={(e) => setG2(Number(e.target.value))}
          className="block w-full mb-2 p-2 border rounded"
        />
        <input
          type="number"
          placeholder="h"
          value={h}
          onChange={(e) => setH(Number(e.target.value))}
          className="block w-full mb-2 p-2 border rounded"
        />
        <input
          type="number"
          placeholder="p"
          value={p2}
          onChange={(e) => setP2(Number(e.target.value))}
          className="block w-full mb-2 p-2 border rounded"
        />
        <button
          onClick={() => setLogResult(babyStepGiantStep(g2, h, p2))}
          className="bg-blue-500 text-white px-4 py-2 rounded mt-2"
        >
          Найти дискретный логарифм
        </button>
        {logResult !== null && (
          <div className="mt-4">
            <strong>Дискретный логарифм:</strong> {logResult} <br />
            <p>Это значение, при котором {g2} в степени {logResult} по модулю {p2} равно {h}.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
