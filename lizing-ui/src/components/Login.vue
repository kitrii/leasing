<template>
  <div class="max-w-md mx-auto mt-20 bg-white p-8 rounded shadow">
    <h2 class="text-2xl font-bold mb-6 text-center text-teal-600">Вход</h2>

    <form @submit.prevent="login" class="flex flex-col gap-4">
      <input type="email" v-model="email" placeholder="Email" class="border p-2 rounded" required />
      <input type="password" v-model="password" placeholder="Пароль" class="border p-2 rounded" required />

      <button type="submit" class="bg-teal-600 text-white p-2 rounded hover:bg-teal-700 transition">Войти</button>
    </form>

    <p class="mt-4 text-center text-gray-600">
      Нет аккаунта? <router-link to="/register" class="text-teal-600 font-bold">Зарегистрироваться</router-link>
    </p>

    <p v-if="message" :class="{'text-green-600': success, 'text-red-600': !success}" class="mt-4 text-center font-semibold">{{ message }}</p>
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
      // сохраняем токен или user_id, если есть
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
