from rest_framework import serializers
from collections import OrderedDict


class GenericSerializer(serializers.ModelSerializer):
	""" Subclass of ModelSerializer """

	def to_representation(self, instance):
		""" Return only not empty fields """
		final_object = super().to_representation(instance)
		# filter null values and create new dict
		final_object = OrderedDict(list(filter(lambda x: x[1], final_object.items())))
		return final_object