extern crate chrono;
extern crate pyo3;
extern crate difference;

use chrono::{DateTime, Utc};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::Python;

use difference::{Changeset, Difference};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};

type VersionId = usize;
type TextData = String;
type Timestamp = DateTime<Utc>;
type FileHistory = Vec<(VersionId, Timestamp, TextData)>;

#[pyclass]
struct VersionControl {
    histories: Arc<Mutex<HashMap<String, FileHistory>>>,
}

#[pymethods]
impl VersionControl {
    #[new]
    fn new() -> Self {
        VersionControl {
            histories: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    fn save_version(&self, path: String, content: String) -> PyResult<()> {
        let mut histories = self.histories.lock().unwrap();
        let history = histories.entry(path).or_insert_with(Vec::new);
        let version_id = history.len() + 1;
        let timestamp = Utc::now();

        history.push((version_id, timestamp, content));
        Ok(())
    }

    fn get_unsaved_changes(&self, path: String, saved_version_id: VersionId) -> PyResult<Vec<PyObject>> {
        let gil = Python::acquire_gil();
        let py = gil.python();
    
        let histories = self.histories.lock().unwrap();
        println!("{}", &path);
        let history = histories.get(&path).ok_or_else(|| {
            PyErr::new::<pyo3::exceptions::PyIndexError, _>("No history available for the specified path")
        })?;
    
        if let Some(&(last_version_id, _, ref last_text)) = history.last() {
            if last_version_id == saved_version_id {
                return Ok(vec![]); 
            }
    
            let saved_text = &history[saved_version_id - 1].2;
            let changeset = Changeset::new(saved_text, last_text, "\n");
    
            let changes: Vec<PyObject> = changeset.diffs.iter().enumerate().map(|(i, diff)| {
                let dict = PyDict::new(py);
                dict.set_item("line", i + 1)?;
                match diff {
                    Difference::Same(ref x) => {
                        dict.set_item("type", "same")?;
                        dict.set_item("text", x)?;
                    },
                    Difference::Add(ref x) => {
                        dict.set_item("type", "add")?;
                        dict.set_item("text", x)?;
                    },
                    Difference::Rem(ref x) => {
                        dict.set_item("type", "remove")?;
                        dict.set_item("text", x)?;
                    }
                }
                Ok(dict.to_object(py))
            }).collect::<PyResult<Vec<PyObject>>>()?;
    
            Ok(changes)
        } else {
            Ok(vec![])
        }
    }
}

#[pyfunction]
fn create_version_control() -> VersionControl {
    VersionControl::new()
}

#[pymodule]
fn vc(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(create_version_control, m)?)?;
    m.add_class::<VersionControl>()?;
    Ok(())
}
