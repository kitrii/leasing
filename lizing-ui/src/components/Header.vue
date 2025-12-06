<template>
  <header class="bg-teal-600 text-white p-4 flex justify-between items-center">
    <h1 class="text-xl font-bold">Лизингомания</h1>
    <button class="bg-red-500 px-3 py-1 rounded" @click="logout">Выйти</button>
  </header>
</template>

<script lang="ts" setup>
const logout = () => {
  // тут будет запрос на FastAPI для выхода
  alert('Выход выполнен (заглушка)')
}
</script>
