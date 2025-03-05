import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles.css';
import { ThemeProvider, createTheme } from "@mui/material/styles";

const theme = createTheme({
    palette: {
        primary: {
            main: "rgb(12, 105, 149)",
        },
        secondary: {
            main: "#1a1f36",
        },
    },
    typography: {
        fontFamily: "Roboto, Arial, sans-serif",
    },
    components: {
        MuiButton: {
            styleOverrides: {
                root: {
                    textTransform: 'none',
                },
            },
        },
    },
});
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <ThemeProvider theme = {theme}>
    <React.StrictMode>
        <App />
    </React.StrictMode>
    </ThemeProvider>
);
