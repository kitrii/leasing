<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-r from-teal-400 to-blue-500 p-4">
    <div class="w-full max-w-md bg-white rounded-xl shadow-lg p-8 animate-fadeIn">
      <h2 class="text-3xl font-bold mb-6 text-center text-teal-600">Вход в Личный кабинет</h2>

      <form @submit.prevent="login" class="flex flex-col gap-4">
        <div class="relative">
          <input
            type="email"
            v-model="email"
            placeholder="Email"
            class="w-full border border-gray-300 p-3 rounded focus:border-teal-500 focus:ring-2 focus:ring-teal-200 transition"
            required
          />
          <span class="absolute right-3 top-3 text-gray-400">
            📧
          </span>
        </div>

        <div class="relative">
          <input
            type="password"
            v-model="password"
            placeholder="Пароль"
            class="w-full border border-gray-300 p-3 rounded focus:border-teal-500 focus:ring-2 focus:ring-teal-200 transition"
            required
          />
          <span class="absolute right-3 top-3 text-gray-400">
            🔒
          </span>
        </div>

        <button
          type="submit"
          class="bg-teal-600 text-white p-3 rounded font-semibold hover:bg-teal-700 transition"
        >
          Войти
        </button>
      </form>

      <p class="mt-4 text-center text-gray-600">
        Нет аккаунта?
        <router-link to="/register" class="text-teal-600 font-bold hover:underline">
          Зарегистрироваться
        </router-link>
      </p>

      <p
        v-if="message"
        :class="success ? 'text-green-600' : 'text-red-600'"
        class="mt-4 text-center font-semibold"
      >
        {{ message }}
      </p>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'

const email = ref('')
const password = ref('')
const message = ref('')
const success = ref(false)

const login = async () => {
  try {
    const res = await fetch('http://127.0.0.1:8000/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value, password: password.value })
    })

    const data = await res.json()
    message.value = data.message
    success.value = res.ok

    if (res.ok) {
      localStorage.setItem('token', data.token)
      setTimeout(() => {
        window.location.href = '/dashboard'
      }, 1000)
    }
  } catch (err) {
    message.value = 'Ошибка сети'
    success.value = false
  }
}
</script>

<style scoped>
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fadeIn {
  animation: fadeIn 0.5s ease-out;
}
</style>
