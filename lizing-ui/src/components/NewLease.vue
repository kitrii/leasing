<template>
  <div class="max-w-lg mx-auto bg-white p-6 rounded-lg shadow-lg">
    <h2 class="text-2xl font-bold mb-4">Создать заявку</h2>
    <form class="space-y-4">
      <input type="text" placeholder="Оборудование" class="w-full p-2 border rounded" />
      <input type="number" placeholder="Аванс" class="w-full p-2 border rounded" />
      <input type="number" placeholder="Срок (мес)" class="w-full p-2 border rounded" />
      <input type="number" step="0.01" placeholder="Ставка (%)" class="w-full p-2 border rounded" />
      <select class="w-full p-2 border rounded">
        <option>Аннуитет</option>
        <option>Дифференцированная</option>
      </select>
      <input type="file" class="w-full" />
      <button type="submit" class="w-full bg-emerald-500 text-white py-2 rounded hover:bg-emerald-600">Отправить</button>
    </form>
  </div>
</template>
