<template>
    <div id="app">
        <h2 class="site-header">Putsync Web UI</h2>
        <el-menu theme="dark" :default-active="active_index" mode="horizontal" @select="handleselect">
            <el-menu-item index="/">Home</el-menu-item>
            <el-menu-item index="/history">History</el-menu-item>
            <el-menu-item index="/statistics">Statistics</el-menu-item>
        </el-menu>

            <el-row>
                <el-col :span="20" :offset="2">
                    <div class="content">
                        <router-view></router-view>
                    </div>
                </el-col>
            </el-row>
    </div>
</template>

<script>
export default {
  data () {
    return {
        active_index: ""
    }
  },

  methods: {
      handleselect(key, key_path) {
          console.log(this.$router);
          this.$router.push({path: key});
      }
  }
}
</script>

<style>
body {
  font-family: Helvetica, sans-serif;
  background-color: #F9FAFC;
}

.content {
    background-color: #FFFFFF;
    padding: 20px;
    border: 1px solid #D3DCE6;
    border-top: none;
}
</style>

<style scoped>
.body {
    margin-top: 20px;
}

.site-header {
}
</style>
