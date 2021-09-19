
module.exports = {
  purge: [
    './src/**/*.html',
  ],
  darkMode: false, // or 'media' or 'class'
  theme: {
    container: {
      center: true,
      padding: '5rem',
    },
    extend: {},
  },
  variants: {
    extend: {},
  },
  plugins: [
      require('daisyui'),
  ],
  daisyui: {
    rtl: false,
    // themes:[
    //     {
    //         'reko': {
    //             // reko-grön                /* your theme name */
    //             'primary' : '#76B82A',           /* Primary color */
    //             'primary-focus' : '#5D9021',     /* Primary color - focused */
    //             'primary-content' : '#ffffff',   /* Foreground content color to use on primary color */

    //             'secondary' : '#00ff00',         /* Secondary color */
    //             'secondary-focus' : '#f3cc30',   /* Secondary color - focused */
    //             'secondary-content' : '#ffffff', /* Foreground content color to use on secondary color */

    //             'accent' : '#37cdbe',            /* Accent color */
    //             'accent-focus' : '#2aa79b',      /* Accent color - focused */
    //             'accent-content' : '#ffffff',    /* Foreground content color to use on accent color */

    //             'neutral' : '#1a5a90',           /* Neutral color */
    //             'neutral-focus' : '#004884',     /* Neutral color - focused */
    //             'neutral-content' : '#ffffff',   /* Foreground content color to use on neutral color */

    //             'base-100' : '#ffffff',          /* Base color of page, used for blank backgrounds */
    //             'base-200' : '#f9fafb',          /* Base color, a little darker */
    //             'base-300' : '#d1d5db',          /* Base color, even more darker */
    //             'base-content' : '#1f2937',      /* Foreground content color to use on base color */

    //             'info' : '#2094f3',              /* Info */
    //             'success' : '#009485',           /* Success */
    //             'warning' : '#ff9900',           /* Warning */
    //             'error' : '#ff5724',             /* Error */
    //         }
    //     }
    // ]
    }
}
