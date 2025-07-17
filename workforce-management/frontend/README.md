
# Workforce Management Frontend (React + TypeScript + Vite)

## Features
- Modern React UI for workforce assignment and optimization
- Gantt chart and table view for assignments
- Legend and color mapping for task types
- Button to re-optimize assignments (calls backend)
- Export Gantt chart as PNG

## Getting Started
1. Install dependencies:
   ```sh
   npm install
   ```
2. Start development server:
   ```sh
   npm run dev
   ```
3. Build for production:
   ```sh
   npm run build
   ```
4. Preview production build:
   ```sh
   npm run preview
   ```

## API Integration
- Connects to backend at `http://localhost:8080/api` for assignments, tasks, workers
- Uses `/api/assignments/optimize` for Gantt chart and re-optimization

## Usage
- By default, shows the Gantt chart with current assignments
- Use the "Re-optimize Assignments" button to update assignments
- Table view and export options available

## Development
- TypeScript, Vite, MUI, Redux
- See `src/components/AssignmentManagement.tsx` for main logic

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default tseslint.config([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
