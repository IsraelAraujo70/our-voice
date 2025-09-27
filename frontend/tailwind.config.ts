import type { Config } from "tailwindcss";
import animate from "tailwindcss-animate";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{ts,tsx,mdx}",
    "./src/components/**/*.{ts,tsx,mdx}",
    "./src/app/**/*.{ts,tsx,mdx}",
  ],
  theme: {
  	container: {
  		center: true,
  		padding: '2rem',
  		screens: {
  			'2xl': '1400px'
  		}
  	},
  	extend: {
  		colors: {
  			// Style.json based colors
  			background: '#0b1220',
  			foreground: '#ffffff',
  			muted: '#9fb3d4',
  			border: 'rgba(255,255,255,0.10)',
  			card: {
  				DEFAULT: 'rgba(255,255,255,0.07)',
  				contrast: 'rgba(255,255,255,0.14)',
  				foreground: '#ffffff'
  			},
  			primary: {
  				DEFAULT: '#3b82f6',
  				foreground: '#ffffff'
  			},
  			secondary: {
  				DEFAULT: 'rgba(255,255,255,0.06)',
  				foreground: '#e6eeff'
  			},
  			accent: {
  				DEFAULT: '#60a5fa',
  				foreground: '#0b1220'
  			},
  			destructive: {
  				DEFAULT: '#ef4444',
  				foreground: '#ffffff'
  			},
  			ring: 'rgba(99, 102, 241, 0.6)',
  			shadow: 'rgba(0, 10, 30, 0.6)',
  			input: 'rgba(255,255,255,0.06)',
  			popover: {
  				DEFAULT: 'rgba(255,255,255,0.07)',
  				foreground: '#ffffff'
  			},
  			chart: {
  				'1': 'hsl(var(--chart-1))',
  				'2': 'hsl(var(--chart-2))',
  				'3': 'hsl(var(--chart-3))',
  				'4': 'hsl(var(--chart-4))',
  				'5': 'hsl(var(--chart-5))'
  			},
  			// Glass effect colors
  			glass: {
  				DEFAULT: 'var(--c-glass)',
  				light: 'var(--c-light)',
  				dark: 'var(--c-dark)',
  				content: 'var(--c-content)',
  				action: 'var(--c-action)',
  				bg: 'var(--c-bg)'
  			}
  		},
  		borderRadius: {
  			sm: '0.5rem',
  			md: '0.8rem',
  			lg: '1.25rem',
  			xl: '2rem',
  			full: '9999px'
  		},
  		backdropBlur: {
  			glass: '8px'
  		},
  		backdropSaturate: {
  			glass: '160%'
  		},
  		fontFamily: {
  			sans: ['"DM Sans"', 'sans-serif']
  		},
  		keyframes: {
  			'accordion-down': {
  				from: {
  					height: '0'
  				},
  				to: {
  					height: 'var(--radix-accordion-content-height)'
  				}
  			},
  			'accordion-up': {
  				from: {
  					height: 'var(--radix-accordion-content-height)'
  				},
  				to: {
  					height: '0'
  				}
  			}
  		},
  		animation: {
  			'accordion-down': 'accordion-down 0.2s ease-out',
  			'accordion-up': 'accordion-up 0.2s ease-out'
  		}
  	}
  },
  plugins: [animate, require("tailwindcss-animate")],
};

export default config;
