import React, { useState } from "react";
import "./App.css";

const App: React.FC = () => {
  // State для быстрой экспоненциации
  const [base, setBase] = useState<bigint>(0n);
  const [exponent, setExponent] = useState<bigint>(0n);
  const [modulus, setModulus] = useState<bigint>(1n);
  const [modExpResult, setModExpResult] = useState<bigint | null>(null);

  // State для расширенного алгоритма Евклида
  const [a, setA] = useState<bigint>(0n);
  const [b, setB] = useState<bigint>(0n);
  const [gcdResult, setGcdResult] = useState<[bigint, bigint, bigint] | null>(
    null
  );

  // State для Диффи-Хеллмана
  const [p, setP] = useState<bigint>(0n);
  const [g, setG] = useState<bigint>(0n);
  const [privateA, setPrivateA] = useState<bigint>(0n);
  const [privateB, setPrivateB] = useState<bigint>(0n);
  const [sharedKey, setSharedKey] = useState<bigint | null>(null);

  // State для алгоритма "Шаг младенца, шаг великана"
  const [g2, setG2] = useState<bigint>(0n);
  const [h, setH] = useState<bigint>(0n);
  const [p2, setP2] = useState<bigint>(0n);
  const [logResult, setLogResult] = useState<bigint | null>(null);

  // Функция быстрого возведения в степень по модулю
  const modExp = (base: bigint, exponent: bigint, modulus: bigint): bigint => {
    if (modulus === 1n) return 0n; // Модуль 1 всегда возвращает 0

    let result = 1n;
    base = ((base % modulus) + modulus) % modulus; // Убедимся, что base неотрицательный

    while (exponent > 0n) {
      if (exponent % 2n === 1n) {
        result = (result * base) % modulus; // Промежуточное умножение, взятое по модулю
      }
      base = (base * base) % modulus; // Промежуточное возведение в квадрат, взятое по модулю
      exponent = exponent / 2n; // Снижаем степень вдвое
    }

    return result;

    /* Возведение в степень по модулю — это вычисление остатка от деления натурального числа a (основание), 
    возведенного в степень n (показатель степени), на натуральное число m (модуль). */
  };

  // Функция расширенного алгоритма Евклида
  const extendedGCD = (a: bigint, b: bigint): [bigint, bigint, bigint] => {
    if (b === 0n) {
      return [a, 1n, 0n];
    }
    const [gcd, x1, y1] = extendedGCD(b, a % b);
    const x = y1;
    const y = x1 - (a / b) * y1;
    return [gcd, x, y];

    // Расширенный алгоритм Евклида — модификация алгоритма Евклида, вычисляющая, кроме наибольшего общего делителя (НОД) целых чисел a, ещё и коэффициенты соотношения Безу
  };

  // Функция Диффи-Хеллмана для генерации общего ключа
  const diffieHellman = (
    p: bigint,
    g: bigint,
    a: bigint,
    b: bigint
  ): bigint => {
    const A = modExp(g, a, p);
    const B = modExp(g, b, p);
    const sharedKey = modExp(B, a, p);
    return sharedKey;

    /* Алгоритм Диффи-Хеллмана — это метод обмена ключами, который позволяет двум сторонам договориться о совместном секретном ключе, 
    используя общедоступные параметры и свойство математического оператора возведения в степень по модулю. 
    Он основан на проблеме дискретного логарифма, которая трудна для решения, но легка для проверки. */
  };

  // Алгоритм «Шаг младенца, шаг великана»
  const babyStepGiantStep = (
    g: bigint,
    h: bigint,
    p: bigint
  ): bigint | null => {
    const m = BigInt(Math.ceil(Math.sqrt(Number(p))));
    const valueMap = new Map<bigint, bigint>();

    // Этап шага младенца
    for (let j = 0n; j < m; j++) {
      const modValue = modExp(g, j, p);
      if (!valueMap.has(modValue)) {
        valueMap.set(modValue, j);
      }
    }

    // Вычисление g^(-m) mod p
    const gInvM = modExp(g, p - 1n - m, p);

    // Этап шага великана
    for (let i = 0n; i < m; i++) {
      const y = (h * modExp(gInvM, i, p)) % p;
      if (valueMap.has(y)) {
        return i * m + valueMap.get(y)!;
      }
    }
    return null; // Если не найден логарифм

    /* Алгоритм «Шаг младенца, шаг великана» (Baby-step Giant-step) — это эффективный метод нахождения дискретного логарифма, 
    который использует пространство и время для оптимизации процесса поиска. 
    В данном алгоритме используется подход с делением на этапы для уменьшения вычислительной сложности задачи нахождения дискретного логарифма. */
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8 flex flex-col items-center justify-center">
      <h1 className="text-3xl font-bold mb-6 text-center">
        Криптографическая библиотека
      </h1>

      {/* Блок для быстрой экспоненциации */}
      <div className="bg-white shadow-lg rounded-lg p-6 mb-6 w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">
          Модульное возведение в степень
        </h2>
        <input
          type="number"
          placeholder="Основание"
          value={base.toString()}
          onChange={(e) => setBase(BigInt(e.target.value))}
          className="block w-full mb-2 p-2 border rounded"
        />
        <input
          type="number"
          placeholder="Показатель степени"
          value={exponent.toString()}
          onChange={(e) => setExponent(BigInt(e.target.value))}
          className="block w-full mb-2 p-2 border rounded"
        />
        <input
          type="number"
          placeholder="Модуль"
          value={modulus.toString()}
          onChange={(e) => setModulus(BigInt(e.target.value))}
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
            <strong>Результат:</strong> {modExpResult.toString()} <br />
            <p>
              Это результат возведения {base.toString()} в степень{" "}
              {exponent.toString()} по модулю {modulus.toString()}.
            </p>
          </div>
        )}
      </div>

      {/* Блок для расширенного алгоритма Евклида */}
      <div className="bg-white shadow-lg rounded-lg p-6 mb-6 w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">Расширенный алгоритм Евклида</h2>
        <input
          type="number"
          placeholder="a"
          value={a.toString()}
          onChange={(e) => setA(BigInt(e.target.value))}
          className="block w-full mb-2 p-2 border rounded"
        />
        <input
          type="number"
          placeholder="b"
          value={b.toString()}
          onChange={(e) => setB(BigInt(e.target.value))}
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
            <strong>НОД:</strong> {gcdResult[0].toString()} <br />
            <strong>x:</strong> {gcdResult[1].toString()} <br />
            <strong>y:</strong> {gcdResult[2].toString()} <br />
            <p>
              НОД ({a.toString()}, {b.toString()}) равен{" "}
              {gcdResult[0].toString()}. Коэффициенты x и y такие, что{" "}
              {a.toString()}*{gcdResult[1].toString()} + {b.toString()}*
              {gcdResult[2].toString()} = {gcdResult[0].toString()}.
            </p>
          </div>
        )}
      </div>

      {/* Блок для Диффи-Хеллмана */}
      <div className="bg-white shadow-lg rounded-lg p-6 mb-6 w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">Обмен ключами Диффи-Хеллмана</h2>
        <input
          type="number"
          placeholder="Простое число p"
          value={p.toString()}
          onChange={(e) => setP(BigInt(e.target.value))}
          className="block w-full mb-2 p-2 border rounded"
        />
        <input
          type="number"
          placeholder="Генератор g"
          value={g.toString()}
          onChange={(e) => setG(BigInt(e.target.value))}
          className="block w-full mb-2 p-2 border rounded"
        />
        <input
          type="number"
          placeholder="Приватный ключ A"
          value={privateA.toString()}
          onChange={(e) => setPrivateA(BigInt(e.target.value))}
          className="block w-full mb-2 p-2 border rounded"
        />
        <input
          type="number"
          placeholder="Приватный ключ B"
          value={privateB.toString()}
          onChange={(e) => setPrivateB(BigInt(e.target.value))}
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
            <strong>Общий ключ:</strong> {sharedKey.toString()} <br />
            <p>
              Этот ключ является результатом обмена ключами между A и B с
              использованием простого числа {p.toString()} и генератора{" "}
              {g.toString()}.
            </p>
          </div>
        )}
      </div>

      {/* Блок для алгоритма "Шаг младенца, шаг великана" */}
      <div className="bg-white shadow-lg rounded-lg p-6 mb-6 w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">
          Алгоритм "Шаг младенца, шаг великана"
        </h2>
        <input
          type="number"
          placeholder="g"
          value={g2.toString()}
          onChange={(e) => setG2(BigInt(e.target.value))}
          className="block w-full mb-2 p-2 border rounded"
        />
        <input
          type="number"
          placeholder="h"
          value={h.toString()}
          onChange={(e) => setH(BigInt(e.target.value))}
          className="block w-full mb-2 p-2 border rounded"
        />
        <input
          type="number"
          placeholder="p"
          value={p2.toString()}
          onChange={(e) => setP2(BigInt(e.target.value))}
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
            <strong>Дискретный логарифм:</strong> {logResult.toString()} <br />
            <p>
              Это значение, при котором {g2.toString()} в степени{" "}
              {logResult.toString()} по модулю {p2.toString()} равно{" "}
              {h.toString()}.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
