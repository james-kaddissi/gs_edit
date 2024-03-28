# gs-edit
GS Edit is a bare bones open source multi language IDE, with the goal of giving all the design and customization of the editor to the user.


Some new core features i've decided on is the implementation of rust into the project. Rust is very impressive in improving python.
The idea is that the base gs-edit will have python managing the frontend and rust managing the backend. This way the project
has easy to code gui with pyqt5, vs more difficult gui if it was all in rust. Perhaps alternate distributions will be made entirely in rust
but for now the main goal is to use rust to cleanup as match of the backend as possible. Power of Rust + Easy to Use Python