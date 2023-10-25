<script setup lang="ts">


</script>

<style scoped>
header {
  background: transparent;
  display: flex;
  padding: 1em;
  gap: 1em;
}

.container{
  display: flex;
  align-items: center;
}
.logo {
  text-align: left;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1em;
}


.text-logo {
  font-family: var(--title-font-family);
  text-align: left;
  font-size: 2rem;
  color: black;
}


.text-logo-annotate {
  font-size: 1.2em;
  padding-left: 1.3em;
  margin-bottom: -1em;
}

.text-logo-reflect {
  font-size: 1.2em;
  padding-left: 1.3em;
  margin-top: 0.5em;
}


@media (max-width: 600px) {
  header {
    flex-direction: column;
  }
}
</style>

<template>
  <header class="container">
    <section class="logo">
      <router-link to="/">
        <img
            src="/images/logo.png"
            alt="Annotate reflect & Repeat"
            width="80"
            height="80"
        />
      </router-link>
      <router-link to="/" style="text-decoration: none;">
      <div class="text-logo">
        <p class="text-logo-annotate">ANNOTATE</p>
        <p class="text-logo-reflect">REFLECT & REPEAT</p>
      </div>
      </router-link>

    </section>
  </header>
</template>
