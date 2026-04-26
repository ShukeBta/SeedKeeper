import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import federation from '@originjs/vite-plugin-federation'
import vuetify from 'vite-plugin-vuetify'

export default defineConfig({
  plugins: [
    vue(),
    vuetify({ autoImport: true }),
    federation({
      name: 'Seedkeeper',
      filename: 'remoteEntry.js',
      exposes: {
        './Page': './src/components/Page.vue',
        './Config': './src/components/Config.vue',
        './Dashboard': './src/components/Dashboard.vue',
        './AppPage': './src/components/AppPage.vue',
      },
      shared: {
        vue: { requiredVersion: false, generate: false },
        vuetify: { requiredVersion: false, generate: false, singleton: true },
        'vuetify/styles': { requiredVersion: false, generate: false, singleton: true },
      },
      format: 'esm'
    })
  ],
  build: {
    target: 'esnext',
    minify: false,
    cssCodeSplit: true,
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@use "@/styles/variables" as *;`,
      }
    },
    postcss: {
      plugins: [
        {
          postcssPlugin: 'internal:charset-removal',
          AtRule: {
            charset: (atRule) => {
              if (atRule.name === 'charset') atRule.remove();
            }
          }
        },
        {
          postcssPlugin: 'vuetify-filter',
          Root(root: any) {
            root.walkRules((rule: any) => {
              if (rule.selector && (
                rule.selector.includes('.v-') || 
                rule.selector.includes('.mdi-')
              )) {
                rule.remove();
              }
            });
          }
        }
      ]
    }
  },
  server: {
    port: 5001,
    cors: true,
    origin: 'http://localhost:5001'
  },
  resolve: {
    alias: {
      '@': '/src'
    }
  }
})
