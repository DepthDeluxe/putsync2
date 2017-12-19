<template>
    <div id="app">
        <el-row>
            <el-col :span="4">
            </el-col>
            <el-col :span="20">
                <el-menu :default-active="active_index" mode="horizontal" @select="handleselect">
                    <h1 class="site-header">Putsync2</h1>
                    <el-menu-item index="/">Home</el-menu-item>
                    <el-menu-item index="/history">History</el-menu-item>
                    <el-menu-item index="/add">Add Magnet Link</el-menu-item>
                    <el-menu-item index="/statistics">Statistics</el-menu-item>
                </el-menu>
            </el-col>
        </el-row>

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
    float: left;
    line-height: 15px;

    margin-right: 25px;
}
</style>
