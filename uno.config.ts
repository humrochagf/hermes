import {
  defineConfig,
  presetUno,
} from 'unocss'

export default defineConfig({
  content: {
    filesystem: [
      'src/hermes/core/templates/*.html',
    ],
  },
  presets: [
    presetUno,
  ],
})
