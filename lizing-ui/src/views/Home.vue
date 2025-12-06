<template>
  <div class="flex flex-col items-center justify-center min-h-screen bg-gradient-to-r from-teal-400 to-blue-500 text-white">
    <h1 class="text-5xl font-bold mb-6">Лизингомания</h1>
    <p class="text-xl mb-8">Управляй лизинговыми заявками быстро и удобно</p>

    <div class="flex gap-4">
      <router-link to="/login" class="px-6 py-3 bg-white text-teal-600 font-bold rounded hover:bg-gray-100 transition">Войти</router-link>
      <router-link to="/register" class="px-6 py-3 bg-white text-teal-600 font-bold rounded hover:bg-gray-100 transition">Регистрация</router-link>
    </div>
  </div>
</template>
