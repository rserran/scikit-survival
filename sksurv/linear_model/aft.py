# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import numpy as np
from sklearn.linear_model import Ridge

from ..base import SurvivalAnalysisMixin
from ..nonparametric import ipc_weights
from ..util import check_array_survival


class IPCRidge(Ridge, SurvivalAnalysisMixin):
    """Accelerated failure time model with inverse probability of censoring weights.

    This model assumes a regression model of the form

    .. math::

        \\log y = \\beta_0 + \\mathbf{X} \\beta + \\epsilon

    L2-shrinkage is applied to the coefficients :math:`\\beta` and
    each sample is weighted by the inverse probability of censoring
    to account for right censoring (under the assumption that
    censoring is independent of the features, i.e., random censoring).

    See [1]_ for further description.

    Parameters
    ----------
    alpha : float, optional, default: 1.0
        Small positive values of alpha improve the conditioning of the problem
        and reduce the variance of the estimates.

    Attributes
    ----------
    coef_ : ndarray, shape = (n_features,)
        Weight vector.

    n_features_in_ : int
        Number of features seen during ``fit``.

    feature_names_in_ : ndarray of shape (`n_features_in_`,)
        Names of features seen during ``fit``. Defined only when `X`
        has feature names that are all strings.

    References
    ----------
    .. [1] W. Stute, "Consistent estimation under random censorship when covariables are
           present", Journal of Multivariate Analysis, vol. 45, no. 1, pp. 89-103, 1993.
           doi:10.1006/jmva.1993.1028.
    """
    def __init__(self, alpha=1.0, fit_intercept=True, normalize="deprecated",
                 copy_X=True, max_iter=None, tol=1e-3, solver="auto"):
        super().__init__(alpha=alpha, fit_intercept=fit_intercept,
                         normalize=normalize, copy_X=copy_X,
                         max_iter=max_iter, tol=tol, solver=solver)

    @property
    def _predict_risk_score(self):
        return False

    def fit(self, X, y):
        """Build an accelerated failure time model.

        Parameters
        ----------
        X : array-like, shape = (n_samples, n_features)
            Data matrix.

        y : structured array, shape = (n_samples,)
            A structured array containing the binary event indicator
            as first field, and time of event or time of censoring as
            second field.

        Returns
        -------
        self
        """
        event, time = check_array_survival(X, y)

        weights = ipc_weights(event, time)
        super().fit(X, np.log(time), sample_weight=weights)

        return self

    def predict(self, X):
        """Predict using the linear accelerated failure time model.

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape = (n_samples, n_features)
            Samples.

        Returns
        -------
        C : array, shape = (n_samples,)
            Returns predicted values on original scale (NOT log scale).
        """
        return np.exp(super().predict(X))

    def score(self, X, y, sample_weight=None):
        return SurvivalAnalysisMixin.score(self, X, y)
