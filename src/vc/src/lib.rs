extern crate pyo3;

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use std::collections::HashMap;
use std::sync::{Arc, Mutex};

#[pyclass]
struct VersionControl {
    versions: Arc<Mutex<HashMap<String, Vec<String>>>>,
}

#[pymethods]
impl VersionControl {
    #[new]
    fn new() -> Self {
        VersionControl {
            versions: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    fn save_version(&self, path: String, content: String) {
        let mut versions = self.versions.lock().unwrap();
        versions.entry(path).or_insert_with(Vec::new).push(content);
    }

    fn get_version(&self, path: String, version_number: usize) -> PyResult<String> {
        let versions = self.versions.lock().unwrap();
        match versions.get(&path) {
            Some(history) if version_number < history.len() => Ok(history[version_number].clone()),
            _ => Err(PyErr::new::<pyo3::exceptions::PyIndexError, _>("Version number out of range")),
        }
    }
}

#[pyfunction]
pub fn create_version_control() -> VersionControl {
    VersionControl::new()
}


#[pymodule]
fn vc(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<VersionControl>()?;
    m.add_function(wrap_pyfunction!(create_version_control, m)?)?;
    Ok(())
}
